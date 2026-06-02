# Vision-Language-Action (VLA) ROS 2 Pipeline

## Overview

This project implements a modular **Vision-Language-Action (VLA)** pipeline using ROS 2 Humble. The system integrates perception, reasoning, and execution into a structured robotics architecture capable of performing pick-and-place tasks in a simulated environment.

The pipeline follows a fully decoupled multi-node architecture:

```
Camera Feed → Perception Node → Reasoning Node → Executor Node → MoveIt 2 / ros2_control
```

---

## System Architecture

### 1. Perception Node (`vla_perception`)

* Subscribes to:

  * `/image_raw` (`sensor_msgs/Image`)
* Performs:

  * Color-based segmentation (red object detection)
  * Centroid extraction (pixel coordinates)
* Publishes:

  * `/detected_object` (`vla_interfaces/DetectedObject`)

Output includes:

* Object label (e.g. `red_block`)
* Pixel coordinates (x, y)
* Confidence score

---

### 2. Reasoning Node (`vla_reasoning`)

* Subscribes to:

  * `/detected_object`
* Performs:

  * Simple task inference logic (rule-based V1)
  * Converts perception output into action plan
* Publishes:

  * `/vla_plan` (`vla_interfaces/VLAPlan`)

Current behavior:

* Detect red block → generate PICK action
* Converts pixel coordinates into approximate world-frame pose

---

### 3. Executor Node (`vla_executor`)

* Subscribes to:

  * `/vla_plan`
* Interfaces with:

  * MoveIt 2 action server (`/move_action`)
* Executes:

  * Cartesian motion goals using `MoveGroup` action
* Supports:

  * PICK (move to detected pose)
  * PLACE (predefined bin location)

Handles:

* Goal submission
* Execution monitoring
* Result logging

---

## Custom Interfaces

### DetectedObject.msg

```
int32 id
string label
float32 x
float32 y
float32 confidence
```

### VLAPlan.msg

```
string action
string target
geometry_msgs/PoseStamped goal_pose
```

---

## Current Capabilities

### ✔ Working Features

* Real-time camera stream processing
* Red object detection (HSV-based segmentation)
* Pixel-to-world approximate mapping
* End-to-end ROS 2 communication pipeline
* MoveIt 2 based trajectory execution
* Modular multi-node architecture

### ⚠ Limitations (Current Version)

* No LLM/VLM integration yet (rule-based reasoning only)
* Simplified 2D → 3D projection (no depth camera fusion)
* Fixed grasp strategy (no grasp synthesis)
* Static bin placement map
* No multi-object task planning

---

## Launch Order (IMPORTANT)

### 1. Start ROS 2 environment

```bash
source /opt/ros/humble/setup.bash
source ~/vla_ws/install/setup.bash
```

---

### 2. Start MoveIt 2 (RViz + robot state)

```bash
ros2 launch moveit_resources_panda_moveit_config demo.launch.py
```

---

### 3. Start perception node

```bash
ros2 run vla_perception perception_node
```

---

### 4. Start reasoning node

```bash
ros2 run vla_reasoning reasoning_node
```

---

### 5. Start executor node

```bash
ros2 run vla_executor vla_executor
```

---

## Topic Graph

```
/image_raw
     ↓
/detected_object
     ↓
/vla_plan
     ↓
MoveIt Action (/move_action)
```

---

## Example Output Flow

### Perception

```
Detected: red_block at (349, 399)
```

### Reasoning

```
PLAN: PICK red_block at (0.34, 0.41)
```

### Executor

```
MoveGroup goal accepted
Execution finished: SUCCESS
```

---

## Requirements

* Ubuntu 22.04
* ROS 2 Humble
* MoveIt 2
* OpenCV
* cv_bridge
* Gazebo / Isaac Sim (optional for simulation)

---

## Future Improvements

* LLM-based reasoning layer (GPT/VLM integration)
* Depth-based 3D reconstruction
* Grasp pose estimation module
* Multi-object task scheduling
* Natural language command interface (ROS 2 Service/Action)
* Failure recovery and replanning

---

## Author

Hridik Kajaria
ROS 2 Robotics Systems – Vision-Language-Action Pipeline
