# SO-101 VR Teleoperation

A Meta Quest 3 XR application built in **Godot 4** that streams real-time hand tracking data (position + orientation) over WebSocket to a ROS 2 pipeline on a host computer intended for robot teleoperation with the SO-101 arm.

> **🚧 Work in Progress** — This project is under active development. The end goal is a complete VR teleoperation system for **bimanual robot arms**, where a user wearing a Meta Quest 3 can intuitively control two robot arms in real time using natural hand and wrist movements.

## Architecture

```
Meta Quest 3 (Godot 4 / OpenXR)
        │
        │  WebSocket (Wi-Fi, port 8765)
        ▼
ROS 2 Node: hand_ws_publisher
  - Listens on ws://0.0.0.0:8765
  - Parses JSON, converts Euler → quaternion
  - Publishes geometry_msgs/PoseStamped to:
      /left_hand_pose
      /right_hand_pose
        │
        ├──▶ ROS 2 Node: hand_pose_subscriber
        │      - Subscribes to both PoseStamped topics
        │      - Prints position + quaternion to console
        │
        └──▶ RViz2
               - Visualises /left_hand_pose  (blue arrow)
               - Visualises /right_hand_pose (orange arrow)
```

## Message Format

Each WebSocket frame is a JSON object (unchanged from Godot):

```json
{
  "left_hand":  { "pos": [x, y, z], "rot": [rx, ry, rz] },
  "right_hand": { "pos": [x, y, z], "rot": [rx, ry, rz] }
}
```

Positions are in metres (Godot world space).  
Rotations are Euler angles **in degrees**, Godot **YXZ** order.

The `hand_ws_publisher` node converts this to `geometry_msgs/PoseStamped`  
(Euler → quaternion, `frame_id = world`) and publishes on  
`/left_hand_pose` and `/right_hand_pose`.

---

## Requirements

### Godot app (Meta Quest 3)
- [Godot 4.x](https://godotengine.org/)
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
git clone https://github.com/mahmoud-maan/SO-101-VR-Teleoperation.git
cd SO-101-VR-Teleoperation
```

### 2. Install the Godot OpenXR Vendors plugin

Open the project in Godot, then go to **AssetLib** and install **Godot OpenXR Vendors**.  
This populates `addons/godotopenxrvendors/.bin/` which is intentionally excluded from git.

### 3. Configure the server IP

In `ws_streamer.gd`, set `server_ip` to your computer's local IP address:

```gdscript
@export var server_ip: String = "192.168.x.x"   # ← change this
@export var server_port: int = 8765
```

Alternatively, set it in the Godot Inspector without editing the file.

### 4. Build and deploy to Quest 3

Follow the [Godot Android export guide](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html).  
Enable **Gradle Build** and target **arm64-v8a**.

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

This starts:
- `hand_ws_publisher` — WebSocket server → `/left_hand_pose`, `/right_hand_pose`
- `hand_pose_subscriber` — prints pose data to console
- `rviz2` — pre-configured with blue (left) and orange (right) pose arrows

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
├── main.gd                  # Initialises OpenXR interface
├── main.tscn                # Root scene
├── ws_streamer.gd           # Reads hand transforms, sends over WebSocket
├── 3d_coordinate.gd/.tscn   # 3-D coordinate visualisation helper
├── openxr_action_map.tres   # OpenXR input action map
├── export_presets.cfg       # Godot Android export configuration
├── addons/
│   └── godotopenxrvendors/  # Plugin metadata (binaries installed separately)
└── ros2_ws/
    └── src/
        └── xr_hand_pipeline/
            ├── launch/
            │   └── hand_pose.launch.py     # Launches all nodes + RViz
            ├── rviz/
            │   └── hand_pose.rviz          # RViz2 config (left=blue, right=orange)
            └── xr_hand_pipeline/
                ├── hand_ws_publisher.py    # WebSocket → PoseStamped publisher
                └── hand_pose_subscriber.py # PoseStamped → console
```

---

