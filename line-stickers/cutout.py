import numpy as np
from PIL import Image
from scipy import ndimage as ndi
im=np.asarray(Image.open('source.png').convert('RGB')).astype(float)
H,W,_=im.shape
mx=im.max(-1);mn=im.min(-1);sat=(mx-mn)/(mx+1)
dark=mx<150
D=3
wall=ndi.binary_dilation(dark,iterations=D)
lab,n=ndi.label(~wall)
border=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
out_reach=np.isin(lab,list(border))
fg=~ndi.binary_dilation(out_reach,iterations=D)  # shrink back
# enclosed light regions to clear: big ones in upper area (arm/racket loop, racket head)
bgcol=(mx>200)&(sat<0.1)
l2,n2=ndi.label(bgcol&fg)
sz=ndi.sum(np.ones_like(mx),l2,range(n2+1));com=ndi.center_of_mass(np.ones_like(mx),l2,range(1,n2+1))
for i in range(1,n2+1):
    cy,cx=com[i-1]
    if cy<480 and cx>380 and not(380<cx<600 and 200<cy<500) and sz[i]>8: fg[l2==i]=False   # racket head + loop

fl,fn=ndi.label(fg);s=ndi.sum(fg,fl,range(fn+1))
fg=np.isin(fl,[i for i in range(1,fn+1) if s[i]>200])
alpha=ndi.gaussian_filter(fg.astype(float),0.7)
out=np.dstack([im,alpha*255]).astype(np.uint8)
Image.fromarray(out).save('cut.png')


