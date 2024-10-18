import numpy as np

def get_q(angle_degrees):
    angle_radians = np.radians(angle_degrees)
    cos_theta = np.cos(angle_radians)
    sin_theta = np.sin(angle_radians)

    rotation_matrix = np.array([
        [cos_theta, -sin_theta, 0],
        [sin_theta, cos_theta, 0],
        [0, 0, 1]
    ])

    quaternion_yaw = np.array([
        np.cos(angle_radians / 2),
        0,
        0,
        np.sin(angle_radians / 2)
    ])

    return quaternion_yaw

def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    ])

if __name__ == '__main__':

    quaternion = [0.5, -0.5, 0.5, -0.5]
    quaternion_yaw = get_q(-120.0)

    new_quaternion = quaternion_multiply(quaternion_yaw, quaternion)
    print(new_quaternion)


