import os
from ament_index_python.packages import get_package_share_directory
from simple_launch import SimpleLauncher, GazeboBridge

# Which world file to load, as a plain Python string (not a launch argument):
# using a LaunchConfiguration substitution here breaks simple_launch's static
# "grep the world name out of the SDF file" detection, which in turn makes
# GazeboBridge fall back to querying a live Gazebo instance that doesn't exist
# yet -> "could not find any Gazebo instance" at launch time.
# Override with: BLUEROV2_WORLD=demo_world.sdf ros2 launch bluerov2_description world_launch.py
WORLD_FILE = os.environ.get('BLUEROV2_WORLD', 'bluerov2_underwater.sdf')

# models/ (e.g. sand_heightmap) are installed flat under this package's share dir;
# the package's own ament resource-path hook is not reliably picked up, so set it explicitly,
# before gz_launch resolves the world file and its includes below.
_pkg_share = get_package_share_directory('bluerov2_description')
_existing = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
os.environ['GZ_SIM_RESOURCE_PATH'] = _pkg_share + (':' + _existing if _existing else '')


def generate_launch_description():

    sl = SimpleLauncher()
    sl.declare_arg('gui', default_value=True)
    sl.declare_arg('spawn', default_value=True)

    with sl.group(if_arg='gui'):
        sl.gz_launch(sl.find('bluerov2_description', WORLD_FILE), "-r")

    with sl.group(unless_arg='gui'):
        sl.gz_launch(sl.find('bluerov2_description', WORLD_FILE), "-r -s")

    bridges = [GazeboBridge.clock(),
               GazeboBridge('/ocean_current', '/current', 'geometry_msgs/Vector3',
                            GazeboBridge.ros2gz)]

    sl.create_gz_bridge(bridges)

    with sl.group(if_arg='spawn'):
        sl.include('bluerov2_description', 'upload_bluerov2_launch.py')

    return sl.launch_description()
