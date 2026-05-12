extends Node

var left_hand: XRController3D
var right_hand: XRController3D

var ws := WebSocketPeer.new()
@export var server_ip: String = "192.168.0.60"
@export var server_port: int = 8765

func _ready():
	left_hand = get_node("../LeftHand")
	right_hand = get_node("../RightHand")

	var server_url = "ws://%s:%d" % [server_ip, server_port]
	var err = ws.connect_to_url(server_url)
	if err != OK:
		print("❌ WebSocket connection failed")
	else:
		print("✅ WebSocket connecting...")

func _process(_delta):
	ws.poll()

	var left_valid := false
	var right_valid := false

	var left_pos: Vector3
	var left_quat: Quaternion
	var right_pos: Vector3
	var right_quat: Quaternion

	if left_hand:
		left_pos = left_hand.global_transform.origin
		left_quat = left_hand.global_transform.basis.get_rotation_quaternion()
		left_valid = true

	if right_hand:
		right_pos = right_hand.global_transform.origin
		right_quat = right_hand.global_transform.basis.get_rotation_quaternion()
		right_valid = true

	if ws.get_ready_state() == WebSocketPeer.STATE_OPEN and left_valid and right_valid:
		var msg = {
			"left_hand": {
				"pos":  [left_pos.x,  left_pos.y,  left_pos.z],
				"quat": [left_quat.x, left_quat.y, left_quat.z, left_quat.w]
			},
			"right_hand": {
				"pos":  [right_pos.x,  right_pos.y,  right_pos.z],
				"quat": [right_quat.x, right_quat.y, right_quat.z, right_quat.w]
			}
		}

		ws.send_text(JSON.stringify(msg))
