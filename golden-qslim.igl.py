import igl
import time
vin,fin = igl.read_triangle_mesh('input_data/upsampled_golden.obj')
start = time.time()
_,vout,fout,_,_ = igl.qslim(vin,fin, 17892)
print("igl qslim time: ", time.time()-start) 
igl.write_triangle_mesh('reference_result/upsample_qslim.obj', vout,fout)
print(fout.shape)
