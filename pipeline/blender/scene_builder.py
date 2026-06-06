"""
scene_builder.py — Blender bpy script
Reads timeline.json and builds the full animated music ball scene.

Usage (headless):
    blender --background --python pipeline/blender/scene_builder.py -- \
        input/audio_stems/song.timeline.json output/renders/song/ "Song Title"

Usage (via MCP / interactive):
    Pass build_scene(timeline, render_dir, title) directly.
"""

import bpy
import math
import json
import sys
import os
from pathlib import Path
from mathutils import Vector


# ─────────────────────────────────────────────
# CONSTANTS (from visual bible)
# ─────────────────────────────────────────────

WALL_COLOR    = (0.83, 0.76, 0.72, 1.0)
LIGHT_COLOR   = (1.0,  0.92, 0.80)
RAIL_COLOR    = (0.85, 0.87, 0.90, 1.0)
RAIL_RADIUS   = 0.006
BALL_RADIUS   = 0.045
PLATFORM_H    = 0.008

BALL_MATERIALS = {
    "blue":   (0.0,  0.72, 0.92, 1.0),
    "green":  (0.3,  0.85, 0.25, 1.0),
    "purple": (0.55, 0.15, 0.85, 1.0),
    "gold":   (0.95, 0.78, 0.10, 1.0),
}

PLATFORM_MATERIALS = {
    "bamboo":  {"color": (0.72, 0.52, 0.18, 1.0), "metallic": 0.2, "roughness": 0.65},
    "chrome":  {"color": (0.85, 0.87, 0.90, 1.0), "metallic": 1.0, "roughness": 0.04},
    "yellow":  {"color": (0.92, 0.86, 0.05, 1.0), "metallic": 0.1, "roughness": 0.55},
    "dark":    {"color": (0.15, 0.15, 0.18, 1.0), "metallic": 0.8, "roughness": 0.15},
}

# Notes per octave mapped to X position spread
NOTE_TO_X = {"C": -0.28, "D": -0.20, "E": -0.12, "F": -0.04,
             "G":  0.04, "A":  0.12, "B":  0.20}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in [bpy.data.meshes, bpy.data.materials,
                  bpy.data.lights, bpy.data.cameras]:
        for item in list(block):
            block.remove(item)


def make_material(name, color, metallic=0.0, roughness=0.5,
                  transmission=0.0, ior=1.45, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value     = color
    bsdf.inputs["Metallic"].default_value       = metallic
    bsdf.inputs["Roughness"].default_value      = roughness
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["IOR"].default_value            = ior
    if emission:
        bsdf.inputs["Emission Color"].default_value  = (*emission[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission[3] if len(emission) > 3 else 1.0
    return mat


def make_glass_marble(name, color_key="blue"):
    color = BALL_MATERIALS.get(color_key, BALL_MATERIALS["blue"])
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=BALL_RADIUS, segments=64, ring_count=32, location=(0, 0, 0)
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    mat = make_material(
        f"MAT_{name}",
        color=color,
        transmission=0.88,
        ior=1.52,
        roughness=0.0,
    )
    obj.data.materials.append(mat)
    return obj


def make_rail_segment(start: Vector, end: Vector, name="RAIL"):
    """Create a chrome tube between two points."""
    mid = (start + end) / 2
    length = (end - start).length
    direction = (end - start).normalized()

    bpy.ops.mesh.primitive_cylinder_add(
        radius=RAIL_RADIUS, depth=length, location=mid
    )
    rail = bpy.context.active_object
    rail.name = name

    # Orient along direction
    rot = direction.to_track_quat('Z', 'Y')
    rail.rotation_euler = rot.to_euler()
    bpy.ops.object.shade_smooth()

    mat = make_material("MAT_chrome", RAIL_COLOR, metallic=1.0, roughness=0.04)
    rail.data.materials.append(mat)
    return rail


def make_platform(location, size=(0.12, 0.035, PLATFORM_H),
                  rotation_z=0.0, mat_type="bamboo", name="PLATFORM"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler.z = rotation_z
    bpy.ops.object.shade_smooth()

    p = PLATFORM_MATERIALS.get(mat_type, PLATFORM_MATERIALS["bamboo"])
    mat = make_material(f"MAT_{name}", p["color"],
                        metallic=p["metallic"], roughness=p["roughness"])
    obj.data.materials.append(mat)
    return obj


def note_to_x(note_name: str) -> float:
    """Convert note name like 'C5' to an X offset on the track."""
    pitch = note_name[0] if note_name else "C"
    octave = int(note_name[1]) if len(note_name) > 1 and note_name[1].isdigit() else 4
    base_x = NOTE_TO_X.get(pitch, 0.0)
    octave_offset = (octave - 4) * 0.56   # one full spread per octave
    return base_x + octave_offset


# ─────────────────────────────────────────────
# SCENE SETUP
# ─────────────────────────────────────────────

def setup_render(scene, resolution=(1080, 1920), samples=96):
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.image_settings.file_format = 'PNG'


def setup_world(scene):
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get("Background") or nt.nodes.new("ShaderNodeBackground")
    bg.inputs[0].default_value = WALL_COLOR
    bg.inputs[1].default_value = 0.35


def add_wall(location=(0, 0.22, 0.5), size=(5, 3)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    wall = bpy.context.active_object
    wall.name = "BG_WALL"
    wall.rotation_euler.x = math.radians(90)
    wall.scale = (size[0], size[1], 1)
    mat = make_material("MAT_wall", WALL_COLOR, roughness=0.92)
    wall.data.materials.append(mat)
    return wall


def add_lighting():
    # Main warm area light (right side)
    bpy.ops.object.light_add(type='AREA', location=(1.5, -0.3, 1.2))
    light = bpy.context.active_object
    light.name = "LIGHT_main"
    light.data.energy = 600
    light.data.color = LIGHT_COLOR
    light.data.size = 0.9
    light.rotation_euler = (math.radians(40), 0, math.radians(-35))

    # Soft fill from left
    bpy.ops.object.light_add(type='AREA', location=(-1.2, -0.4, 0.8))
    fill = bpy.context.active_object
    fill.name = "LIGHT_fill"
    fill.data.energy = 120
    fill.data.color = (0.9, 0.93, 1.0)
    fill.data.size = 1.2


def add_camera(target: Vector, distance=0.9, height_offset=0.1):
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Camera"

    cam_pos = target + Vector((0.05, -distance, height_offset))
    cam.location = cam_pos
    cam.data.lens = 85

    direction = (target - cam_pos).normalized()
    rot = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot.to_euler()
    cam.rotation_euler.z += math.radians(5)   # Dutch tilt

    bpy.context.scene.camera = cam
    return cam


# ─────────────────────────────────────────────
# TRACK BUILDER — events → 3D layout
# ─────────────────────────────────────────────

def build_track(events: list, ball_color="blue") -> dict:
    """
    Place platforms and rails from a list of timeline events.
    Returns a dict mapping event index → (platform, rail) objects.
    """
    objects = {}
    prev_pos = None

    for i, ev in enumerate(events):
        note = ev.get("note", "C4")
        velocity = ev.get("velocity", 0.5)
        t = ev.get("time", i * 0.5)

        # Descend Z over time (ball travels down the track)
        z = 0.6 - (i * 0.08)
        x = note_to_x(note)

        plat_pos = Vector((x, 0.0, z))
        platform = make_platform(
            location=plat_pos,
            size=(0.10 + velocity * 0.04, 0.032, PLATFORM_H),
            rotation_z=math.radians(note_to_x(note) * 15),
            mat_type="bamboo",
            name=f"PLATFORM_{i:03d}",
        )
        objects[i] = {"platform": platform, "pos": plat_pos}

        # Rail connecting previous platform to this one
        if prev_pos is not None:
            start = prev_pos + Vector((0, 0, 0))
            end   = plat_pos + Vector((0, 0, 0))
            make_rail_segment(start, end, name=f"RAIL_{i:03d}")

        prev_pos = plat_pos

    return objects


def animate_ball(ball, track_objects: dict, events: list, fps=30):
    """
    Keyframe ball position along the track, synced to event times.
    """
    ball.animation_data_create()
    ball.animation_data.action = bpy.data.actions.new(f"{ball.name}_action")

    for i, ev in enumerate(events):
        if i not in track_objects:
            continue
        plat_pos = track_objects[i]["pos"]
        # Ball sits just above platform
        ball_z = plat_pos.z + PLATFORM_H + BALL_RADIUS
        frame = int(ev["time"] * fps)

        ball.location = (plat_pos.x, plat_pos.y - 0.01, ball_z)
        ball.keyframe_insert(data_path="location", frame=frame)

        # Squash on impact: slightly flatten then restore
        ball.scale = (1.0, 1.0, 1.0)
        ball.keyframe_insert(data_path="scale", frame=max(0, frame - 1))
        ball.scale = (1.12, 1.12, 0.85)
        ball.keyframe_insert(data_path="scale", frame=frame)
        ball.scale = (1.0, 1.0, 1.0)
        ball.keyframe_insert(data_path="scale", frame=frame + 3)

    # Smooth interpolation
    if ball.animation_data and ball.animation_data.action:
        for fcurve in ball.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'


def animate_camera(cam, track_objects: dict, events: list, fps=30):
    """
    Smooth camera follow — lags slightly behind ball position.
    """
    cam.animation_data_create()
    cam.animation_data.action = bpy.data.actions.new("Camera_action")

    for i, ev in enumerate(events):
        if i not in track_objects:
            continue
        target = track_objects[i]["pos"]
        frame = int(ev["time"] * fps) + 8   # slight lag

        cam_pos = target + Vector((0.05, -0.9, 0.12))
        cam.location = cam_pos
        cam.keyframe_insert(data_path="location", frame=frame)

    if cam.animation_data and cam.animation_data.action:
        for fcurve in cam.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def build_scene(timeline: dict, render_dir: str, title: str,
                ball_color="blue", samples=96):
    scene = bpy.context.scene
    clear_scene()

    setup_render(scene, samples=samples)
    setup_world(scene)
    add_wall()
    add_lighting()

    events = timeline.get("events", [])
    fps = 30
    scene.frame_start = 1
    total_frames = int(timeline.get("duration", 30) * fps)
    scene.frame_end = total_frames

    # Build 3D track
    track_objects = build_track(events, ball_color=ball_color)

    # Marble
    ball = make_glass_marble("MARBLE_01", ball_color)
    if events and 0 in track_objects:
        start_pos = track_objects[0]["pos"]
        ball.location = (start_pos.x, start_pos.y - 0.01,
                         start_pos.z + PLATFORM_H + BALL_RADIUS)

    animate_ball(ball, track_objects, events, fps)

    # Camera — aim at first event or scene center
    if 0 in track_objects:
        cam_target = track_objects[0]["pos"] + Vector((0, 0, BALL_RADIUS))
    else:
        cam_target = Vector((0, 0, 0.4))

    cam = add_camera(cam_target)
    animate_camera(cam, track_objects, events, fps)

    # Save .blend
    Path(render_dir).mkdir(parents=True, exist_ok=True)
    blend_path = str(Path(render_dir) / "scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Render
    scene.render.filepath = str(Path(render_dir) / "frame_")
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(animation=True, write_still=False)

    print(f"Scene built: {len(events)} events | {total_frames} frames | {render_dir}")
    return {"events": len(events), "frames": total_frames, "blend": blend_path}


# ─────────────────────────────────────────────
# CLI entry point (headless blender call)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        if len(args) >= 2:
            timeline_path = args[0]
            render_dir    = args[1]
            title         = args[2] if len(args) > 2 else "Music Ball"

            with open(timeline_path) as f:
                timeline = json.load(f)

            build_scene(timeline, render_dir, title)
        else:
            print("Usage: blender --background --python scene_builder.py -- "
                  "<timeline.json> <render_dir/> [title]")
