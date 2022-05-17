import numpy as np
import re
import subprocess
import igl

basepath = '/home/zhongshi/Workspace/wmtk-freeze/build_release/'

apps = dict(remesh='app/remeshing_app',
            tetra='app/tetwild/tetwild',
            harmo='app/harmonic_tet/wmtk_harmonic_tet_bin',
            sec='app/sec_app')


def scale(x):
    scale.a = x.min(axis=0)
    y = x-scale.a
    scale.b = y.max()
    y = y/scale.b
    return y


def use_scale(x): return (x-scale.a)/scale.b


def parse_log(regex, loglist):
    rec = re.compile(regex)
    timer = []
    for t, f in loglist:
        with open(f, 'r') as fp:
            matches = ([l for l in fp.readlines()
                        if rec.match(l) is not None])
            assert len(matches) == 1
            time = float(rec.match(matches[0]).group(1))
            timer.append((t, time))
    print(timer)
    np.savetxt("timer.csv", np.asarray(timer), delimiter=",")


def write_unit_scale_file(ref, output):
    v, _ = igl.read_triangle_mesh(ref)
    scale(v)

    v1, f1 = igl.read_triangle_mesh(output)
    igl.write_triangle_mesh(output + '.unit.ply', use_scale(v1), f1)


def slicetmesh(tetv, tett, clipper):
    # clipper = np.array([0.9, 0.4,0.7,-2.8]) octocat
    mesh_faces = igl.boundary_facets(tett)

    def clip_and_color():
        bc = igl.barycenter(tetv, tett)
        x, y, z = tetv[tett].mean(axis=1).T
        # print((bc*clipper[:3]).sum(axis=1))
        clip_index = (bc*clipper[:3]).sum(axis=1) + clipper[3] >= 0
        # print(clip_index)
        # clip_index = np.where(0.9*x + 0.4*y + 0.7*z - 2.8 >= 0)[0]

        fc = igl.boundary_facets(tett[clip_index])

        original_faces = set(tuple(sorted(f)) for f in mesh_faces)
        from_facet = [i for i, f in enumerate(
            fc) if tuple(sorted(f)) in original_faces]
        return tetv, fc, from_facet

    V, F, facet = clip_and_color()
    marker = np.zeros(len(F))
    marker[facet] = 1
    return V, F, marker


def plot_clip(V, F, marker):
    colorA = np.array([192, 192, 192])/256
    colorB = np.array([249, 161, 94])/256

    full_color = np.tile(colorA, (F.shape[0], 1))
    full_color[marker == 1] = colorB

    plt = None
    sh = dict(width=1000, height=1000, wireframe=True)
    vw = mp.Viewer(sh)
    vw.add_mesh(V, F, c=full_color, shading=sh)
    plt = mp.Subplot(plt, vw, s=[1, 2, 1])
    vw = mp.Viewer(sh)

class common_process:
    @classmethod
    def outpath(c):
        return f'{c.base}/out/'

    @classmethod
    def logpath(c):
        return f'{c.base}/log/'

    @classmethod
    def log_info(c):
        parse_log(c.timer_regex, [
                  (t, f'{c.logpath()}/{t}.log') for t in c.threads])

    @classmethod
    def blender_preprocess(c, t=0):
        write_unit_scale_file(c.input, f'{c.outpath()}/{t}.obj')
        subprocess.run('blender -b render.blend -P blender.py',
                       shell=True, cwd=c.base)