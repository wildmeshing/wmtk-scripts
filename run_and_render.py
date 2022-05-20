import meshio
import numpy as np
import igl
import re
import subprocess

from utils import *


class fig1_fat(common_process):
    base = 'fig1-fat/'
    threads = [0, 1, 2, 4, 8, 16, 32]
    input = f'input_data/39507.stl'

    timer_regex = r"^.*total time (.*)s$"

    @classmethod
    def run_tw(cls):
        t = 10
        exe = apps['tetra']
        output = f'{cls.outpath()}/{t}.tetra.msh'
        params = [basepath + exe, '-i', cls.input, '-o', output] + \
            f'-j {t} --max-its 25 --filter-with-input'.split()
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
    def run_qslim(cls):
        t = 32
        exe = apps['qslim']
        output = f'{cls.outpath()}/{t}.qslim.obj'
        params = [basepath + exe, cls.input, output] + \
            f'-j {t} -t 5e-3'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.qslim.log', 'w') as fp:
            subprocess.run(params, stdout=fp)

    @classmethod
    def run_secenv(cls):
        t = 32
        exe = apps['sec']
        output = f'{cls.outpath()}/{t}.sec.obj'
        params = [basepath + exe, cls.input, output] + \
            f'-e 1e-2 -j {t} -t 1e-3'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.sec.log', 'w') as fp:
            subprocess.run(params, stdout=fp)

    @classmethod
    def run_harmo(cls):
        t = 32
        inp = f'{cls.outpath()}/10.tetra.msh_final.msh'
        output = f'{cls.outpath()}/{t}.harmo.msh'
        params = [basepath + apps['harmo'], inp, output] + \
            f'-j {t}'.split()
        print(' '.join(params))
        with open(f'{cls.logpath()}/{t}.harmo.log', 'w') as fp:
            subprocess.run(params, stdout=fp)

    @classmethod
    def run(cls):
        cls.run_tw()
        cls.run_harmo()
        cls.run_remenv()
        cls.run_qslim()

    @classmethod
    def log_info(c):
        for key in ['tetra', 'sec', 'harmo', 'remesh']:
            timer = parse_log(c.timer_regex, [
                (t, f'{c.logpath()}/{t}.{key}.log') for t in c.threads])
            np.savetxt(f"{c.base}/timer.{key}.csv",
                       np.asarray(timer), delimiter=",")
            plot_scatter(f'{c.base}/scale.{key}.svg', np.asarray(timer))

    @classmethod
    def blender_process(c, t=32):
        v, f = igl.read_triangle_mesh(c.input)
        scale(v)
        blfile = f'{c.base}/render.blend'

        blend_surf_file(blfile, (use_scale(v), f), f'{c.base}/input.png', plot_edge=False)
        
        for key in ['qslim' , 'remesh']:
            v1, f1 = igl.read_triangle_mesh(f'{c.outpath()}/{t}.{key}.obj')
            blend_surf_file(blendfile=f'{c.base}/render.blend', obj=(
                use_scale(v1), f1), png=f'{c.base}/{key}.png', plot_edge=True)

        slice_and_render(blfile, 
        mesh=f'{c.outpath()}/10.tetra.msh_final.msh',
         slicer=[0.27, 1, 0.35, -6.6], pngpath=f'{c.base}/tetra.png')
        slice_and_render(blfile, 
        mesh=f'{c.outpath()}/32.harmo.msh',
         slicer=[0.27, 1, 0.35, -6.6], pngpath=f'{c.base}/harmo.png')

class fig3_sec(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig3-statue-sec/'
    input = f'input_data/Sapphos_Head.stl'
    timer_regex = r"^.*runtime (.*)$"
    timer_unit = 1e-3
    exe = apps['sec']
    reference = 'reference_result/sec-statue-igl.obj'

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.obj'
            params = [basepath + cls.exe, cls.input,
                      output] + f'-j {t}'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)
        



class fig3_qslim(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig3-qslim/'
    input = f'input_data/48013.stl'
    timer_regex = r"^.*runtime (.*)$"
    timer_unit = 1e-3
    exe = apps['qslim']
    reference = 'reference_result/qslim-golden-igl.obj'

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.obj'
            params = [basepath + cls.exe, cls.input,
                      output] + f'-j {t}'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)


class fig4_rem(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig4-hellskull-UniRem/'
    input = f'input_data/hellSkull_126k.stl'
    timer_regex = r"^.*runtime (.*)$"
    timer_unit = 1e-3
    exe = apps['remesh']

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.obj'
            params = [basepath + cls.exe, cls.input, output] + \
                f'-j {t} -r 0.01 -f 0'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)


class fig4_lucy_rem(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig4-lucy-UniRem/'
    input = f'input_data/120628.stl'
    timer_regex = r"^.*runtime (.*)$"
    timer_unit = 1e-3
    exe = apps['remesh']
    reference = 'reference_result/OpenFlipper_lucy_9.obj'

    @classmethod
    def run(cls, threads=None):
        if threads is None:
            threads = cls.threads
        for t in threads:
            output = f'{cls.outpath()}/{t}.obj'
            params = [basepath + cls.exe, cls.input, output] + \
                f'-j {t} -r 0.01 -f 0'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)


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
    def blender_process(c, t=32):
        outname = 'reference_result/reference-res.msh'
        m = meshio.read(outname)
        tetv, tett = m.points, m.cells[0].data
        tetv = scale(tetv)
        V, F, marker = slicetmesh(tetv, tett, [-1, 0, 0, 0.8])
        blend_surf_file(blendfile=f'{c.base}/render.blend', obj=(V, F[marker == 0]), png=f'{c.base}/ref.png',
                        plot_edge=True)

        outname = f'{c.outpath()}/{t}.msh'
        m = meshio.read(outname)
        tetv, tett = m.points, m.cells[0].data
        tetv = scale(tetv)
        V, F, marker = slicetmesh(tetv, tett, [-1, 0, 0, 0.8])
        blend_surf_file(blendfile=f'{c.base}/render.blend', obj=(V, F[marker == 0]), png=f'{c.base}/out.png',
                        plot_edge=True)


class fig6_tw(common_process):
    base = 'fig6-octocat-tw/'
    threads = [0, 1, 2, 4, 8, 16, 32]
    input = f'input_data/dragon.off'
    exe = apps['tetra']
    timer_regex = r"^.*total time (.*)s$"

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.msh'
            params = [basepath + cls.exe, '-i', cls.input, '-o', output] + \
                f'-j {t} --max-its 10'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)

    @classmethod
    def blender_process(c, t=0):
        v, _ = igl.read_triangle_mesh(c.input)
        scale(v)

        slice_and_render(blendfile=f'{c.base}/render.blend', mesh=f'{c.outpath()}/{t}.msh_final.msh',
         slicer=[0, 0, -1, 0], pngpath=f'{c.base}/out.png')

class fig6_tw_sample(common_process):
    base = 'fig6-tw-sample/'
    threads = [0, 1, 2, 4, 8, 16, 32]
    input = f'input_data/dragon.off'
    exe = apps['tetra']
    timer_regex = r"^.*total time (.*)s$"

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.msh'
            params = [basepath + cls.exe, '-i', cls.input, '-o', output] + \
                f'-j {t} --max-its 10 --sample-envelope'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)

    @classmethod
    def blender_process(c, t=0):
        v, f = igl.read_triangle_mesh(c.input)
        scale(v)
        blend_surf_file(blendfile=f'{c.base}/render.blend', obj=(scale(v), f), png=f'{c.base}/input.png', plot_edge=False)

        slice_and_render(blendfile=f'{c.base}/render.blend', mesh='reference_result/dragon.msh',
         slicer=[0, 0, -1, 0], pngpath=f'{c.base}/tetwild.png')
        slice_and_render(blendfile=f'{c.base}/render.blend', mesh=f'{c.outpath()}/{t}.msh_final.msh',
         slicer=[0, 0, -1, 0], pngpath=f'{c.base}/out.png')

class fig7_secenv(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig7-eins-secenv/'
    input = f'input_data/einstein_big.stl'
    timer_regex = r"^.*runtime (.*)$"
    timer_unit = 1e-3
    exe = apps['sec']

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.obj'
            params = [basepath + cls.exe, cls.input, output] + \
                f'-e 1e-3 -j {t} -t 1e-2'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)


class fig8_rem_env(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig8-headported-UniRemEnv/'
    input = f'input_data/head_-_ported_-_scaled.stl'
    timer_regex = r"^.*runtime (.*)$"
    timer_unit = 1e-3
    exe = apps['remesh']

    @classmethod
    def run(cls):
        for t in cls.threads[::-1]:
            output = f'{cls.outpath()}/{t}.obj'
            params = [basepath + cls.exe, cls.input, output] + \
                f'-e 1e-3 -j {t} -r 0.01 -f 0'.split()
            print(' '.join(params))
            with open(f'{cls.logpath()}/{t}.log', 'w') as fp:
                subprocess.run(params, stdout=fp)





if __name__ == '__main__':
    for f in [fig3_sec, fig3_qslim, fig4_lucy_rem, fig7_secenv, fig8_rem_env]:
        f.log_info();
    #fig3_sec, fig3_    /qslim, fig3_sec, fig4_lucy_rem, fig6_tw, fig7_secenv, fig5_harmo,
    # fig6_tw_sample
    # v,f = igl.read_triangle_mesh(fig6_tw_sample.input)
    # fig1_fat.run_harmo()

    