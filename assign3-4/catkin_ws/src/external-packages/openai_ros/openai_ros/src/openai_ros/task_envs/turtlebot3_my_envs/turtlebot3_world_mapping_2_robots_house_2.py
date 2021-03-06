import os

import turtlebot3_world_mapping_2_robots

class TurtleBot3WorldMapping2RobotsHouse2Env(turtlebot3_world_mapping_2_robots.TurtleBot3WorldMapping2RobotsEnv):
    def __init__(self):
        # Export TB3 robots position to ENV variable so they can be accessible in the launch file
        os.environ["GAZEBO_WORLD"] = "house-2.world"

        os.environ["FIRST_TB3_X"] = "0.5"
        os.environ["FIRST_TB3_Y"] = "0.0"
        os.environ["FIRST_TB3_Z"] = "0.0"
    
        os.environ["SECOND_TB3_X"] = "-0.5"
        os.environ["SECOND_TB3_Y"] = "0.0"
        os.environ["SECOND_TB3_Z"] = "0.0"

        self.actual_map_file = "house-2_walkable.pgm"

        super(TurtleBot3WorldMapping2RobotsHouse2Env, self).__init__("turtlebot3_world_mapping_default.yaml")
