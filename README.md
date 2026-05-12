# VR Hand Pose Tracking to ROS 2 Bridge

A **Meta Quest 3** XR application built in **Godot 4.6** that streams real-time hand/controller tracking data (position + orientation) over WebSocket to a **ROS 2** pipeline on a host computer, where poses are visualised in **RViz2**.

This project is a self-contained bridge between a VR headset and ROS 2. It is intended as a foundation for downstream applications such as robot teleoperation.

---

## Architecture

```
Meta Quest 3 (Godot 4.6 / OpenXR)
        │
        │  WebSocket — Wi-Fi, port 8765
        │  JSON: { pos: [x,y,z], quat: [x,y,z,w] }
        ▼
ROS 2 Node: hand_ws_publisher
  - Receives JSON over WebSocket
  - Remaps coordinate frame: Godot (Y-up) → ROS REP-103 (Z-up)
  - Publishes geometry_msgs/PoseStamped:
      /left_hand_pose
      /right_hand_pose
        │
        ├──▶ ROS 2 Node: hand_pose_subscriber
        │      Prints position + quaternion to console
        │
        └──▶ RViz2
               Displays both hand poses as live 3-axis coordinate frames
```

---

## Message Format

Each WebSocket frame sent from Godot is a JSON object:

```json
{
  "left_hand":  { "pos": [x, y, z], "quat": [x, y, z, w] },
  "right_hand": { "pos": [x, y, z], "quat": [x, y, z, w] }
}
```

- `pos` — position in metres, Godot world space (Y-up)
- `quat` — orientation as quaternion `[x, y, z, w]`, Godot world space

The `hand_ws_publisher` node converts both into ROS REP-103 convention before publishing:

```
Godot → ROS position:     ros_x = -godot_z
                          ros_y = -godot_x
                          ros_z =  godot_y

Godot → ROS orientation:  q_ros = Q_GODOT_TO_ROS * q_godot
                          where Q_GODOT_TO_ROS = (0.5, -0.5, -0.5, 0.5)
```

---

## Requirements

### Godot app (Meta Quest 3)
- [Godot 4.6](https://godotengine.org/)
- **Godot OpenXR Vendors** plugin — install from the Godot Asset Library
  *(Project → Asset Library → search "Godot OpenXR Vendors")*
- Android export template with Gradle build enabled

### ROS 2 pipeline (host computer)
- ROS 2 Jazzy (or later)
- Python package: `websockets`

```bash
pip install websockets
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/mahmoud-maan/vr-hand-bridge.git
cd vr-hand-bridge
```

### 2. Install the Godot OpenXR Vendors plugin

Open the project in Godot, go to **AssetLib** and install **Godot OpenXR Vendors**.
This populates `addons/godotopenxrvendors/.bin/` which is intentionally excluded from git.

### 3. Configure the server IP

In `ws_streamer.gd`, set `server_ip` to your computer's local IP address:

```gdscript
@export var server_ip: String = "192.168.x.x"   # ← change this
@export var server_port: int = 8765
```

You can also set this in the Godot Inspector without editing the file.

### 4. Build and deploy to Quest 3

Follow the [Godot Android export guide](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html).
Enable **Gradle Build**.

---

## Running the ROS 2 Pipeline

```bash
cd ros2_ws

# Build (first time or after changes)
colcon build
source install/setup.bash
```

### Option A — Launch everything at once (publisher + subscriber + RViz)

```bash
ros2 launch xr_hand_pipeline hand_pose.launch.py
```

Starts:
- `hand_ws_publisher` — WebSocket server → publishes `/left_hand_pose`, `/right_hand_pose`
- `hand_pose_subscriber` — prints pose data to console
- `rviz2` — pre-configured, shows both hands as live 3-axis coordinate frames

### Option B — Run nodes individually

```bash
# Terminal 1 — WebSocket server + ROS publisher
ros2 run xr_hand_pipeline hand_ws_publisher

# Terminal 2 — subscriber (prints hand poses)
ros2 run xr_hand_pipeline hand_pose_subscriber

# Terminal 3 — RViz visualisation
rviz2 -d $(ros2 pkg prefix xr_hand_pipeline)/share/xr_hand_pipeline/rviz/hand_pose.rviz
```

Start the Godot app on the Quest 3 after the publisher node is running.

---

## Project Structure

```
.
├── main.gd                        # Initialises OpenXR interface
├── main.tscn                      # Root scene
├── ws_streamer.gd                 # Reads hand transforms, sends over WebSocket
├── 3d_coordinate.gd/.tscn         # 3-D coordinate visualisation helper
├── openxr_action_map.tres         # OpenXR input action map
├── export_presets.cfg             # Godot Android export configuration
├── addons/
│   └── godotopenxrvendors/        # Plugin metadata (binaries installed separately)
└── ros2_ws/
    └── src/
        └── xr_hand_pipeline/
            ├── launch/
            │   └── hand_pose.launch.py     # Launches all nodes + RViz
            ├── rviz/
            │   └── hand_pose.rviz          # RViz2 config — 3-axis frames per hand
            └── xr_hand_pipeline/
                ├── hand_ws_publisher.py    # WebSocket → PoseStamped (with frame remap)
                └── hand_pose_subscriber.py # PoseStamped → console
```

