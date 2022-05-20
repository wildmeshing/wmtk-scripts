import shutil
import plotly
import plotly.graph_objects as go
import numpy as np
import re
import subprocess
import igl

plotly.io.orca.config.use_xvfb = True

basepath = '/home/zhongshi/Workspace/wildmeshing-toolkit/buildr/'

apps = dict(remesh='app/remeshing_app',
            tetra='app/tetwild/tetwild',
            harmo='app/harmonic_tet/wmtk_harmonic_tet_bin',
            qslim='app/qslim_app',
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
    return (timer)


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
        timer = parse_log(c.timer_regex, [
            (t, f'{c.logpath()}/{t}.log') for t in c.threads])
        np.savetxt(f"{c.base}/timer.csv", np.asarray(timer), delimiter=",")
        plot_scatter(f'{c.base}/scale.svg', np.asarray(timer))

    @classmethod
    def blender_process(c, t=0):
        write_unit_scale_file(c.input, f'{c.outpath()}/{t}.obj')
        blend_surf_file(f'{c.base}/render.blend', f'{c.outpath()}/{t}.obj.unit.ply',
                        f'{c.base}/out.png', plot_edge=True)
        render_input(c)




def plot_scatter(filename, timer):
    histocolor = 'rgb(162, 155, 254)'

    go.Figure(go.Scatter(x=timer[1:, 0], y=timer[1:, 1], mode='markers+lines',
                         marker_line_width=4.5, marker_size=8,
                         marker=dict(color=histocolor))
              ).update_layout(xaxis_type="log", yaxis_type='log',
                              paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)',
                              yaxis=dict(gridcolor='grey',
                                         gridwidth=0.5, zeroline=True),
                              geo=dict(showframe=True)
                              ).write_image(filename)

import tempfile

def blend_surf_file(blendfile, obj, png, plot_edge=False):
    with open('blender_surf.pyt') as fp:
        lines = [l for l in fp.readlines()]
    with tempfile.TemporaryDirectory() as tmpdirname:
        if type(obj) is not str:
            v,f = obj
            igl.write_triangle_mesh(tmpdirname + '/obj.ply', v, f)
            obj = tmpdirname + '/obj.ply'
        print('Reading files here ', obj)
        with open(tmpdirname + '/blender.py','w') as fout:
            fout.write(f'in_name, out_png = "{obj}", "{png}"\n')
            fout.write(f'PLOT_EDGE = {plot_edge}\n')
            fout.writelines(lines)
        subprocess.run(f'blender -b {blendfile} -P {tmpdirname}/blender.py', shell=True) 

import meshio
def slice_and_render(blendfile, mesh, slicer, pngpath):
    # v, _ = igl.read_triangle_mesh(c.input)
    # scale(v)

    m = meshio.read(mesh)
    tetv, tett = m.points, m.cells[0].data
    V, F, marker = slicetmesh(tetv, tett, slicer)
    V = use_scale(V)

    with open('blender_slice.pyt') as fp:
        lines = [l for l in fp.readlines()]
    with tempfile.TemporaryDirectory() as tmpdirname:
        obj0, obj1 = tmpdirname + '/slice0.ply', tmpdirname + '/slice1.ply'
        igl.write_triangle_mesh(obj0, V, F[marker == 0])
        igl.write_triangle_mesh(obj1, V, F[marker == 1])
        with open(tmpdirname + '/blender.py','w') as fout:
            fout.write(f'cut_name, sf_name, out_png = "{obj0}", "{obj1}", "{pngpath}"\n')
            fout.write(f'PLOT_EDGE = True\n')
            fout.writelines(lines)
        subprocess.run(f'blender -b {blendfile} -P {tmpdirname}/blender.py', shell=True) 

def render_input(cls):
    v, f = igl.read_triangle_mesh(cls.input)
    v = scale(v)
    blend_surf_file(cls.base + '/render.blend',
                    (v, f), cls.base + '/input.png')
            
    if cls.reference is not None:
        v1, f1 = igl.read_triangle_mesh(cls.reference)
        blend_surf_file(cls.base + '/render.blend',
                    (use_scale(v1), f1), cls.base + '/ref.png', plot_edge=True)
