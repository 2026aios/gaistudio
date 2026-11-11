"""綠幕去背並切成 6 格（2x3），輸出 cells/cell_N.png（保留每格原本位置，以利保持跳躍高度）"""
import os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE=os.path.dirname(os.path.abspath(__file__))
im=np.asarray(Image.open(os.path.join(HERE,'sheet.webp')).convert('RGB')).astype(float)
r,g,b=im[...,0],im[...,1],im[...,2]
spill=g-np.maximum(r,b)
a=np.clip(1-(spill-25)/(90-25),0,1)          # 綠色越純越透明
a=ndi.grey_opening(a,size=(2,2))
rgb=im.copy(); rgb[...,1]=np.minimum(g,np.maximum(r,b)+8)  # 去綠邊
out=np.dstack([rgb,a*255]).astype(np.uint8)
os.makedirs(os.path.join(HERE,'cells'),exist_ok=True)
H,W=a.shape; ch,cw=H//2,W//3
for k in range(6):
    rr,cc=divmod(k,3)
    cell=Image.fromarray(out[rr*ch:(rr+1)*ch,cc*cw:(cc+1)*cw])
    # 移除小雜點
    al=np.asarray(cell)[...,3]>40; lab,n=ndi.label(al); s=ndi.sum(al,lab,range(n+1))
    keep=np.isin(lab,[i for i in range(1,n+1) if s[i]>60])
    arr=np.asarray(cell).copy(); arr[...,3]=np.where(keep|(arr[...,3]<=40),arr[...,3],0)*(ndi.binary_dilation(keep,iterations=2))
    cell=Image.fromarray(arr); cell.save(os.path.join(HERE,'cells',f'cell_{k+1}.png'))
    print(k+1,cell.getbbox())
