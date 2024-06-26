import os
import numpy as np
import nibabel as nib
import SimpleITK as sitk
from rivuletpy.rivulet import rtrace


def loadswc(filepath):
    '''
    Load swc file as a N X 7 numpy array
    '''
    swc = []
    with open(filepath) as f:
        lines = f.read().split("\n")
        for l in lines:
            if not l.startswith('#'):
                cells = l.split(' ')
                if len(cells) == 7:
                    cells = [float(c) for c in cells]
                    # cells[2:5] = [c-1 for c in cells[2:5]]
                    swc.append(cells)
    return np.array(swc)

def getarray(swcdata,shape):
    array=np.zeros(shape)
    lid = swcdata[:, 0]
    for i in range(swcdata.shape[0]):
        # Change color if its a bifurcation
        # if (swcdata[i, 0] == swcdata[:, -1]).sum() > 1:
        #     line_color = [random(), random(), random()]

        # Draw a line between this node and its parent
        if i < swcdata.shape[0] - 1 and swcdata[i, -1] == swcdata[i + 1, 0]:
            # print("dot:",np.array([swcdata[i, 2],swcdata[i, 3],swcdata[i, 4]]))
            x=(int)(round(swcdata[i, 2]))
            y =(int)(round(swcdata[i, 3]))
            z =(int)(round(swcdata[i, 4]))
            r = (int)(round(swcdata[i, 5]))#swcdata[i, 5]
            array[x,y,z]=r
        else:
            pid = swcdata[i, -1]
            pidx = np.argwhere(pid == lid).flatten()
            if len(pidx) == 1:
                pidx=pidx[0]
                dotnum=round(max(abs(swcdata[pidx, 2] - swcdata[i, 2]) / 0.1,abs(swcdata[pidx, 3] - swcdata[i, 3]) / 0.1,abs(swcdata[pidx, 4] - swcdata[i, 4]) / 0.1))
                r=(int)(round((swcdata[i, 5]+swcdata[pidx, 5])/2))#(swcdata[i, 5]+swcdata[pidx, 5])/2
                # print(swcdata[i, 2],swcdata[pidx, 2])
                # print(dotnum)
                xa = np.linspace(round(swcdata[i, 2]), round(swcdata[pidx, 2]),num=dotnum)
                ya = np.linspace(round(swcdata[i, 3]), round(swcdata[pidx, 3]),num=dotnum)
                za = np.linspace(round(swcdata[i, 4]), round(swcdata[pidx, 4]),num=dotnum)
                # print("dot1:",np.array([swcdata[i, 2],swcdata[i, 3],swcdata[i, 4]]))
                # print("dot2:",np.array([swcdata[pidx, 2],swcdata[pidx, 3],swcdata[pidx, 4]]))
                for (x,y,z) in zip(xa,ya,za):
                    x = (int)(round(x))
                    y = (int)(round(y))
                    z = (int)(round(z))
                    array[x, y, z] = r
    return  array


label_dir = '/media/DataA/LiverVessel/test_dataset/private/label'
label_paths = [os.path.join(label_dir, x)
                    for x in os.listdir(label_dir)
                    if x.endswith('.nii.gz')]
label_paths.sort()
print(label_paths)
for idx in range(len(label_paths)):
    name = label_paths[idx].split('/')[-1].split('.')[0]
    print(name)
    #根据label得到血管分别的swc文件
    rtrace('/media/DataA/LiverVessel/test_dataset/private/label/' + name +'.nii.gz','/media/DataA/LiverVessel/test_dataset/private/CLine/' + name + '.txt' )
    #得到图像尺寸
    img = nib.load(label_paths[idx])
    data = img.get_fdata()
    affine = img.affine

    #swc转为矩阵
    swcdata = loadswc('/media/DataA/LiverVessel/test_dataset/private/CLine/' + name + '.txt')
    img_arr = getarray(swcdata,data.shape)
    img_arr[img_arr > 1] = 1
    #保存
    centerline = nib.Nifti1Image(img_arr,affine)
    saved_img = nib.save(centerline,'/media/DataA/LiverVessel/test_dataset/private/CLine/' + name + '.nii.gz')
    print('*****************************************************{} finished'.format(name))


