extends Node3D

# var decimal_places: int = 2

@onready var _label_x: Label3D = $XAxis/XLabel
@onready var _label_y: Label3D = $YAxis/YLabel
@onready var _label_z: Label3D = $ZAxis/Label3D


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	var pos := global_position
	
	_label_x.text = "X: %.2f" % pos.x
	_label_y.text = "Y: %.2f" % pos.y
	_label_z.text = "Z: %.2f" % pos.z
