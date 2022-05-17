import meshio
import numpy as np
import igl
import re
import subprocess

from run_utils import *

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


class fig5_harmo(common_process):
    base = 'fig5-gauss-harm/'
    threads = [0, 1, 2, 4, 8, 16, 32]
    input = f'input_data/gaussian_points_1M.ply'
    exe = apps['harmo']
    timer_regex = r"^.*Time cost: (.*)$"

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.msh'
            params = [basepath + cls.exe, cls.input, output] + \
                f'--harmonize -j {t}'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)

    @classmethod
    def blender_preprocess(c, t=0):
        outname = f'{c.outpath()}/{t}.msh'
        m = meshio.read(outname)
        tetv, tett = m.points, m.cells[0].data
        tetv = scale(tetv)
        V, F, marker = slicetmesh(tetv, tett, [-1,0,0,0.5])
        igl.write_triangle_mesh(outname + '.slice.ply',V, F[marker==0])
        subprocess.run('blender -b render.blend -P blender.py', shell=True, cwd=c.base)
    


class fig6_tw(common_process):
    base = 'fig6-octocat-tw/'
    threads = [0, 1, 2, 4, 8, 16, 32]
    input = f'input_data/32770.stl'
    exe = apps['tetra']
    timer_regex = r"^.*total time (.*)s$"

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.msh'
            params = [basepath + cls.exe, '-i',cls.input, '-o',output] + \
                f'-j {t} --max-its 10'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)

    @classmethod
    def blender_preprocess(c, t=0):
        v, _ = igl.read_triangle_mesh(c.input)
        scale(v)

        outname = f'{c.outpath()}/{t}.msh_final.msh'
        m = meshio.read(outname)
        tetv, tett = m.points, m.cells[0].data

        V, F, marker = slicetmesh(tetv, tett, [0.9, 0.4,0.7,-2.8])
        V = use_scale(V)
        igl.write_triangle_mesh(outname + '.slice0.ply',V, F[marker==0])
        igl.write_triangle_mesh(outname + '.slice1.ply',V, F[marker==1])
        subprocess.run('blender -b render.blend -P blender.py', shell=True, cwd=c.base)

class fig1_fat(common_process):
    base = 'fig1-fat/'
    threads = [0, 1, 2, 4, 8, 16, 32]
    input = f'input_data/39507.stl'
    
    timer_regex = r"^.*total time (.*)s$"

    @classmethod
    def run_tw(cls):
        t = 32
        exe = apps['tetra']
        output = f'{cls.outpath()}/{t}.tetra.msh'
        params = [basepath + exe, '-i',cls.input, '-o',output] + \
            f'-j {t} --max-its 25 --sample-envelope --filter-with-input'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.tw.log', 'w') as fp:
            subprocess.run(params, stdout=fp)

    @classmethod
    def run_remenv(cls):
        t = 32
        exe = apps['remesh']
        output = f'{cls.outpath()}/{t}.remesh.obj'
        params = [basepath + exe, cls.input, output] + \
            f'-e 1e-3 -j {t} -r 0.01 -f 0'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
            subprocess.run(params, stdout=fp)
    
    @classmethod
    def run_secenv(cls):
        t = 32
        exe = apps['sec']
        output = f'{cls.outpath()}/{t}.sec.obj'
        params = [basepath + exe, cls.input, output] + \
            f'-e 1e-3 -j {t} -t 1e-2'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.sec.log', 'w') as fp:
            subprocess.run(params, stdout=fp)

    @classmethod
    def run_harmo(cls):
        t = 32
        output = f'{cls.outpath()}/{t}.harmo.msh'
        params = [basepath + apps['harmo'], cls.input, output] + \
            f'--harmonize -j {t}'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
            subprocess.run(params, stdout=fp)

    @classmethod
    def run_all(cls):
        cls.run_tw()
        cls.run_harmo()
        cls.run_secenv()
        cls.run_remenv()

    @classmethod
    def blender_preprocess(c, t=0):
        v, _ = igl.read_triangle_mesh(c.input)
        scale(v)

        outname = f'{c.outpath()}/{t}.msh_final.msh'
        m = meshio.read(outname)
        tetv, tett = m.points, m.cells[0].data

        V, F, marker = slicetmesh(tetv, tett, [0.27, 1, 0.35, -6.6])
        V = use_scale(V)
        igl.write_triangle_mesh(outname + '.slice0.ply',V, F[marker==0])
        igl.write_triangle_mesh(outname + '.slice1.ply',V, F[marker==1])
        subprocess.run('blender -b render.blend -P blender.py', shell=True, cwd=c.base)
   
if __name__ == '__main__':
    # fig6_tw.blender_preprocess(0)
    fig1_fat.run()
    fig1_fat.blender_preprocess(0)