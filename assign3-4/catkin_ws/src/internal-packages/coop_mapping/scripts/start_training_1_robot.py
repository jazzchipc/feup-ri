#!/usr/bin/env python

import os
import gym
import numpy
import time
import qlearn
from gym import wrappers
# ROS packages required
import rospy
import rospkg
from openai_ros.openai_ros_common import StartOpenAI_ROS_Environment

VS_ROS_DEBUG = 1

if __name__ == '__main__':

    if VS_ROS_DEBUG:
        raw_input('Waiting for VS ROS debugger to be attached... Press a key once it has been attached.')

    ### Export ENV variables BEGIN
    
    # Add node name to ROS logging messages 
    os.environ['ROSCONSOLE_FORMAT']='[${severity}] [${time}]: ${node}: ${message}'
    
    # Set TB3 model
    os.environ['TURTLEBOT3_MODEL'] = 'burger'
    
    ### Export ENV variables END

    rospy.init_node('turtlebot3_world_mapping_qlearn', anonymous=True, log_level=rospy.DEBUG)

    # Init OpenAI_ROS ENV
    task_and_robot_environment_name = rospy.get_param(
        '/turtlebot3/task_and_robot_environment_name')
    env = StartOpenAI_ROS_Environment(
        task_and_robot_environment_name)
    # Create the Gym environment
    rospy.loginfo("Gym environment done")
    rospy.loginfo("Starting Learning")

    # Set the logging system
    rospack = rospkg.RosPack()
    pkg_path = rospack.get_path('coop_mapping')
    outdir = pkg_path + '/training_results'
    env = wrappers.Monitor(env, outdir, force=True)
    rospy.loginfo("Monitor Wrapper started")

    last_time_steps = numpy.ndarray(0)

    # Loads parameters from the ROS param server
    # Parameters are stored in a yaml file inside the config directory
    # They are loaded at runtime by the launch file
    Alpha = rospy.get_param("/turtlebot3/alpha")
    Epsilon = rospy.get_param("/turtlebot3/epsilon")
    Gamma = rospy.get_param("/turtlebot3/gamma")
    epsilon_discount = rospy.get_param("/turtlebot3/epsilon_discount")
    nepisodes = rospy.get_param("/turtlebot3/nepisodes")
    nsteps = rospy.get_param("/turtlebot3/nsteps")

    running_step = rospy.get_param("/turtlebot3/running_step")

    # Initialises the algorithm that we are going to use for learning
    qlearn = qlearn.QLearn(actions=range(env.action_space.n),
                           alpha=Alpha, gamma=Gamma, epsilon=Epsilon)
    initial_epsilon = qlearn.epsilon

    start_time = time.time()
    highest_reward = 0

    # Starts the main training loop: the one about the episodes to do
    for x in range(nepisodes):
        rospy.loginfo("############### START EPISODE=>" + str(x))

        cumulated_reward = 0
        done = False
        if qlearn.epsilon > 0.05:
            qlearn.epsilon *= epsilon_discount

        # Initialize the environment and get first state of the robot
        observation = env.reset()
        state = ''.join(map(str, observation))

        # Show on screen the actual situation of the robot
        # env.render()
        # for each episode, we test the robot for nsteps
        for i in range(nsteps):
            rospy.logwarn("############### Start Step=>" + str(i))
            rospy.loginfo("Choosing next action...")
            # Pick an action based on the current state
            action = qlearn.chooseAction(state)
            rospy.loginfo("Next action is:%d", action)
            # Execute the action in the environment and get feedback
            observation, reward, done, info = env.step(action)

            rospy.loginfo(str(observation) + " " + str(reward))
            cumulated_reward += reward
            if highest_reward < cumulated_reward:
                highest_reward = cumulated_reward

            nextState = ''.join(map(str, observation))

            # Make the algorithm learn based on the results
            rospy.loginfo("# state we were=>" + str(state))
            rospy.loginfo("# action that we took=>" + str(action))
            rospy.loginfo("# reward that action gave=>" + str(reward))
            rospy.loginfo("# episode cumulated_reward=>" + str(cumulated_reward))
            rospy.loginfo("# State in which we will start next step=>" + str(nextState))
            qlearn.learn(state, action, reward, nextState)

            if not (done):
                rospy.loginfo("NOT DONE")
                state = nextState
            else:
                rospy.loginfo("DONE")
                last_time_steps = numpy.append(last_time_steps, [int(i + 1)])
                break
            rospy.logwarn("############### END Step=>" + str(i))
            #raw_input("Next Step...PRESS KEY")
            # rospy.sleep(2.0)
        m, s = divmod(int(time.time() - start_time), 60)
        h, m = divmod(m, 60)
        rospy.logerr(("EP: " + str(x + 1) + " - [alpha: " + str(round(qlearn.alpha, 2)) + " - gamma: " + str(
            round(qlearn.gamma, 2)) + " - epsilon: " + str(round(qlearn.epsilon, 2)) + "] - Reward: " + str(
            cumulated_reward) + "     Time: %d:%02d:%02d" % (h, m, s)))

    rospy.loginfo(("\n|" + str(nepisodes) + "|" + str(qlearn.alpha) + "|" + str(qlearn.gamma) + "|" + str(
        initial_epsilon) + "*" + str(epsilon_discount) + "|" + str(highest_reward) + "| PICTURE |"))

    l = last_time_steps.tolist()
    l.sort()

    # print("Parameters: a="+str)
    rospy.loginfo("Overall score: {:0.2f}".format(last_time_steps.mean()))
    rospy.loginfo("Best 100 score: {:0.2f}".format(reduce(lambda x, y: x + y, l[-100:]) / len(l[-100:])))

    env.close()