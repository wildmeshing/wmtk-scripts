import numpy as np
import re
import subprocess
import igl

basepath = '/home/zhongshi/Workspace/wmtk-freeze/buildr/'

apps = dict(remesh='app/Release/remeshing_app',
            tetra='app/tetwild/Release/tetwild',
            harmo='app/harmonic_tet/Release/wmtk_harmonic_tet_bin',
            sec='app/Release/sec_app')


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


class fig3_sec(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig3-statue-sec/'
    input = f'input_data/Sapphos_Head.stl'
    timer_regex = r"^.*runtime (.*)$"
    exe = apps['sec']

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


class fig7_secenv(common_process):
    threads = [0, 1, 2, 4, 8, 16, 32]
    base = 'fig7-eins-secenv/'
    input = f'input_data/einstein_big.stl'
    timer_regex = r"^.*runtime (.*)$"
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
    fig4_rem.run()
    fig4_rem.log_info()
