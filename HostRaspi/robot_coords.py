import numpy as np

np.seterr(all="ignore")
async def Ailink6dofelephant(xd, yd, zd, horient):
    GG = []
    objh = np.eye(4)
    objh[0:3, 0:3] = horient
    objh[0, 3] = xd
    objh[1, 3] = yd
    objh[2, 3] = zd
    d1 = 131.56
    d4 = 66.39
    d5 = 73.18
    d6 = 43.6
    a2 = 110.4
    a3 = 96
    px = xd
    py = yd
    pz = zd
    nx = horient[0, 0]
    ny = horient[1, 0]
    nz = horient[2, 0]
    ox = horient[0, 1]
    oy = horient[1, 1]
    oz = horient[2, 1]
    ax = horient[0, 2]
    ay = horient[1, 2]
    az = horient[2, 2]
    n = px - d6 * ax
    m = py - d6 * ay
    u = np.sqrt(m**2 + n**2 - d4**2)
    G = np.zeros(6)
    # Solution 1: use positive u
    try:
        G[0] = np.arctan2(((m / n) - (d4 / u)), (1 + (m / n) * (d4 / u)))
        C1 = np.cos(G[0])
        S1 = np.sin(G[0])
        G[5] = np.arctan2((C1 * oy - S1 * ox), (S1 * nx - C1 * ny))
        G[4] = np.arcsin(C1 * ay - S1 * ax)
        C6 = np.cos(G[5])
        S6 = np.sin(G[5])
        th234 = np.arctan2((C1 * S6 * nx + S1 * S6 * ny + C1 * C6 * ox + S1 * C6 * oy), (-S6 * nz - C6 * oz))
        r14 = n * C1 + m * S1 + d5 * np.sin(th234)
        r34 = pz - d6 * az - d1 - d5 * np.cos(th234)
        G[2] = np.arccos((r14**2 + r34**2 - a3**2 - a2**2) / (2 * a3 * a2))
        C3 = np.cos(G[2])
        S3 = np.sin(G[2])
        G[1] = np.arctan2(-(r14 * (a2 + a3 * C3) + r34 * a3 * S3), (r34 * (a2 + a3 * C3) - r14 * a3 * S3))
        G[3] = th234 - G[1] - G[2]
        x, y, z, h = flink6dofelephant(G[0], G[1], G[2], G[3], G[4], G[5])
        if np.sum(np.sum(np.abs(h - objh))) < 0.2:
            GG.append(G)
    except Exception as e:
        pass
    # Solution 2: negative acos
    try:
        G[2] = -np.arccos((r14**2 + r34**2 - a3**2 - a2**2) / (2 * a3 * a2))
        C3 = np.cos(G[2])
        S3 = np.sin(G[2])
        G[1] = np.arctan2(-(r14 * (a2 + a3 * C3) + r34 * a3 * S3), (r34 * (a2 + a3 * C3) - r14 * a3 * S3))
        G[3] = th234 - G[1] - G[2]
        x, y, z, h = flink6dofelephant(G[0], G[1], G[2], G[3], G[4], G[5])
        if np.sum(np.sum(np.abs(h - objh))) < 0.2:
            GG.append(G)
    except Exception as e:
        pass
    
    # Solution 3: use negative -u
    try:
        G[0] = np.arctan2(((m / n) - d4 / (-u)), (1 + (m / n) * (d4 / (-u))))
        C1 = np.cos(G[0])
        S1 = np.sin(G[0])
        G[5] = np.arctan2((C1 * oy - S1 * ox), (S1 * nx - C1 * ny))
        G[4] = np.arcsin(C1 * ay - S1 * ax)
        C6 = np.cos(G[5])
        S6 = np.sin(G[5])
        th234 = np.arctan2((C1 * S6 * nx + S1 * S6 * ny + C1 * C6 * ox + S1 * C6 * oy), (-S6 * nz - C6 * oz))
        r14 = n * C1 + m * S1 + d5 * np.sin(th234)
        r34 = pz - d6 * az - d1 - d5 * np.cos(th234)
        G[2] = np.arccos((r14**2 + r34**2 - a3**2 - a2**2) / (2 * a3 * a2))
        C3 = np.cos(G[2])
        S3 = np.sin(G[2])
        G[1] = np.arctan2(-(r14 * (a2 + a3 * C3) + r34 * a3 * S3), (r34 * (a2 + a3 * C3) - r14 * a3 * S3))
        G[3] = th234 - G[1] - G[2]
        x, y, z, h = flink6dofelephant(G[0], G[1], G[2], G[3], G[4], G[5])
        if np.sum(np.sum(np.abs(h - objh))) < 0.2:
            GG.append(G)
    except Exception as e:
        pass
    
    # Solution 4: use negative acos
    try:
        G[2] = -np.arccos((r14**2 + r34**2 - a3**2 - a2**2) / (2 * a3 * a2))
        C3 = np.cos(G[2])
        S3 = np.sin(G[2])
        G[1] = np.arctan2(-(r14 * (a2 + a3 * C3) + r34 * a3 * S3), (r34 * (a2 + a3 * C3) - r14 * a3 * S3))
        G[3] = th234 - G[1] - G[2]
        x, y, z, h = flink6dofelephant(G[0], G[1], G[2], G[3], G[4], G[5])

        if np.sum(np.sum(np.abs(h - objh))) < 0.2:
            GG.append(G)
    except Exception as e:
        pass
    
    # Find the best solution
    GGmin = np.inf
    k = 0
    for i in range(len(GG)):
        if np.sum(np.abs(GG[i])) < GGmin:
            GGmin = np.sum(np.abs(GG[i]))
            k = i
    if not GG:
        print("Object is out of range!")
        return None, True
    G = GG[k]
    return G, False

def flink6dofelephant(theta1, theta2, theta3, theta4, theta5, theta6):

    d1 = 131.56
    d4 = 66.39
    d5 = 73.18
    d6 = 43.6
    a2 = 110.4
    a3 = 96
    h = trans(theta1, d1, 0, np.pi / 2) @ trans(theta2 - np.pi / 2, 0, -a2, 0) @ trans(theta3, 0, -a3, 0) @ trans(theta4 - np.pi / 2, d4, 0, np.pi / 2) @ trans(theta5 + np.pi / 2, d5, 0, -np.pi / 2) @ trans(theta6, d6, 0, 0)
    x = h[0, 3]
    y = h[1, 3]
    z = h[2, 3]
    return x, y, z, h

def trans(theta, d, a, alpha):
    T = np.array([
        [np.cos(theta), -np.sin(theta) * np.cos(alpha), np.sin(theta) * np.sin(alpha), a * np.cos(theta)],
        [np.sin(theta), np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), a * np.sin(theta)],
        [0, np.sin(alpha), np.cos(alpha), d],
        [0, 0, 0, 1]
    ])
    return T
