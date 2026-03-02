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

	var left_pos: Vector3
	var left_rot: Vector3
	var right_pos: Vector3
	var right_rot: Vector3

	var left_valid := false
	var right_valid := false

	if left_hand:
		left_pos = left_hand.global_transform.origin
		left_rot = left_hand.global_transform.basis.get_euler()
		left_valid = true

		#print("Left Hand - Position: (%.3f, %.3f, %.3f) Rotation: (%.3f, %.3f, %.3f)" %
			#[left_pos.x, left_pos.y, left_pos.z,
			 #rad_to_deg(left_rot.x), rad_to_deg(left_rot.y), rad_to_deg(left_rot.z)])

	if right_hand:
		right_pos = right_hand.global_transform.origin
		right_rot = right_hand.global_transform.basis.get_euler()
		right_valid = true

		#print("Right Hand - Position: (%.3f, %.3f, %.3f) Rotation: (%.3f, %.3f, %.3f)" %
			#[right_pos.x, right_pos.y, right_pos.z,
			 #rad_to_deg(right_rot.x), rad_to_deg(right_rot.y), rad_to_deg(right_rot.z)])

	# Send only if socket is open and we have valid data
	if ws.get_ready_state() == WebSocketPeer.STATE_OPEN and left_valid and right_valid:
		var msg = {
			"left_hand": {
				"pos": [left_pos.x, left_pos.y, left_pos.z],
				"rot": [
					rad_to_deg(left_rot.x),
					rad_to_deg(left_rot.y),
					rad_to_deg(left_rot.z)
				]
			},
			"right_hand": {
				"pos": [right_pos.x, right_pos.y, right_pos.z],
				"rot": [
					rad_to_deg(right_rot.x),
					rad_to_deg(right_rot.y),
					rad_to_deg(right_rot.z)
				]
			}
		}

		ws.send_text(JSON.stringify(msg))
