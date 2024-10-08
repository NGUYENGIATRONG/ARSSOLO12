
import simulation.solo12_pybullet_env as e
import argparse
from fabulous.color import blue, green, red, bold
import numpy as np
import math

PI = np.pi

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--PolicyDir', help='directory of the policy to be tested', type=str, default='24_07_5')
    parser.add_argument('--FrictionCoeff', help='foot friction value to be set', type=float, default=1.6)
    parser.add_argument('--WedgeIncline', help='wedge incline degree of the wedge', type=int, default=11)
    parser.add_argument('--WedgeOrientation', help='wedge orientation degree of the wedge', type=float, default=0)
    parser.add_argument('--MotorStrength', help='maximum motor Strength to be applied', type=float, default=7.0)
    parser.add_argument('--RandomTest', help='flag to sample test values randomly ', type=bool, default=False)
    parser.add_argument('--seed', help='seed for the random sampling', type=float, default=100)
    parser.add_argument('--EpisodeLength', help='number of gait steps of a episode', type=int, default=30000)
    parser.add_argument('--Downhill', help='should robot walk downhill?', type=bool, default=False)
    parser.add_argument('--PerturbForce',
                        help='perturbation force to applied perpendicular to the heading direction of the robot',
                        type=float, default=0.0)
    parser.add_argument('--Stairs', help='test on staircase', type=bool, default=False)
    parser.add_argument('--AddImuNoise', help='flag to add noise in IMU readings', type=bool, default=False)
    parser.add_argument('--Test', help='Test without data', type=bool, default=False)

    args = parser.parse_args()
    policy = np.load("experiments/" + args.PolicyDir + "/iterations/matrix_20x11.npy")
    WedgePresent = True
    if args.WedgeIncline == 0:
        WedgePresent = False
    elif args.WedgeIncline < 0:
        args.WedgeIncline = -1 * args.WedgeIncline
        args.Downhill = True

    env = e.Solo12PybulletEnv(render=True,
                       wedge=WedgePresent,
                       stairs=args.Stairs,
                       downhill=args.Downhill,
                       seed_value=args.seed,
                       on_rack=False,
                       gait='trot',
                       default_pos=(-0.27, 0, 0.2))

    if args.RandomTest:
        env.randomize_only_inclines(default=False)
    else:
        env.incline_deg = args.WedgeIncline
        env.incline_ori = np.radians(args.WedgeOrientation)
        env.SetFootFriction(args.FrictionCoeff)
        env.clips = args.MotorStrength
        env.perturb_steps = 300
        env.y_f = args.PerturbForce

    state = env.reset()
    print(
        bold(blue("\nTest Parameters:\n")),
        green('\nWedge Inclination:'), red(env.incline_deg),
        green('\nWedge Orientation:'), red(math.degrees(args.WedgeOrientation)),
        green('\nCoeff. of friction:'), red(env.friction),
        green('\nMotor saturation torque:'), red(env.clips))

    # Simulation starts
    t_r = 0
    for i_step in range(args.EpisodeLength):
        action = policy.dot(state)
        state, r, _, angle = env.step(action)
        t_r += r

    print("Total_reward " + str(t_r))
