import os, glob, sys, time
import json
import xmltodict
import cv2
import shutil

ignore_diff=True

classes=['person', 'face', 'employee_card', 'practising_certificate', 'contract', 'identity_card']
stage=sys.argv[1]
f ="/media/haria/data/MobileNet-YOLO/data/VOCdevkit/VOC2007/ImageSets/"+stage+".txt"
dirname = os.path.dirname(os.path.dirname(f))
rootdir = os.path.dirname(dirname)
jpegfolder = os.path.join(dirname,"JPEGImages")
annofolder = os.path.join(dirname,"Annotations")
print (rootdir, jpegfolder, annofolder)
annotations = [l.decode().strip() for l in open(f,"rb").readlines()]

for annotation in annotations:
    labels = "VOC/labels/"+stage+"/"+annotation.replace("/","_") + ".txt"
    images = "VOC/images/"+stage+"/"+annotation.replace("/","_") + ".jpg"
    
    if not os.path.exists(os.path.dirname(labels)):
        os.makedirs(os.path.dirname(labels))
    
    if not os.path.exists(os.path.dirname(images)):
        os.makedirs(os.path.dirname(images))
    
    xml = os.path.join(annofolder, annotation+".xml")
    jpeg = os.path.join(jpegfolder, annotation.replace(".xml",".jpg")+".jpg")
    #print (gindex, xml, jpeg)
    try:
        assert(os.path.exists(xml))
        assert (os.path.exists(jpeg))
    except:
        print(xml)
        print(jpeg)
        continue
        
    data = xmltodict.parse(open(xml,"rb").read())
    # xml = xmltodict.unparse(mydict, pretty=True, full_document=False)

    jdata = json.loads(json.dumps(data))

    im = cv2.imread(jpeg)
    h,w,c = im.shape
    try:
        width = int(jdata["annotation"]["size"]["width"])
        height = int(jdata["annotation"]["size"]["height"])
        if not w==width:
            print (w, width)
        if not h==height:
            print(h, height)
    except:
        print("size check error", xml)
        continue
    
    h = float(h)
    w = float(w)
    keeps=[]

    if "bndbox" in jdata["annotation"]["object"]:
        obj = jdata["annotation"]["object"]
        if obj["name"] not in classes:
            continue
        x1 = float(obj["bndbox"]["xmin"])
        y1 = float(obj["bndbox"]["ymin"])
        x2 = float(obj["bndbox"]["xmax"])
        y2 = float(obj["bndbox"]["ymax"])
        x1 = x1 if (x1>=1) else 1
        y1 = y1 if (y1>=1) else 1
        x2 = x2 if (x2<w) else (w-1)
        y2 = y2 if (y2<h) else (h-1)
        bbox_w = x2 - x1
        bbox_h = y2 - y1

        x1 = x1/w
        x2 = x2/w
        y1 = y1/h 
        y2 = y2/h
        center_x = (x1 + x2)/2.0
        center_y = (y1 + y2)/2.0
        ww = bbox_w/w
        hh = bbox_h/h

        if (x2==0) or (x2 <=x1) or (x2> w) or (y2>h):
            print(xml, obj)
        else:
             keeps.append("%d %06f %06f %06f %06f\n" % (classes.index(obj["name"]), center_x, center_y, ww, hh))
    else:
        for obj in jdata["annotation"]["object"]:
            if obj["name"] not in classes:
                continue
            x1 = float(obj["bndbox"]["xmin"])  
            y1 = float(obj["bndbox"]["ymin"]) 
            x2 = float(obj["bndbox"]["xmax"]) 
            y2 = float(obj["bndbox"]["ymax"])
            x1 = x1 if (x1>=0) else 0
            y1 = y1 if (y1>=0) else 0
            x2 = x2 if (x2<w) else (w-1)
            y2 = y2 if (y2<h) else (h-1)
            bbox_w = x2 - x1
            bbox_h = y2 - y1

            x1 = x1/w
            y1 = y1/h
            x2 = x2/w
            y2 = y2/h
            center_x = (x1 + x2)/2.0
            center_y = (y1 + y2)/2.0
            ww = bbox_w/w
            hh = bbox_h/h

            if (x2==0) or (x2 <=x1) or (x2> w) or (y2>h):
                print(xml, obj)
            keeps.append("%d %06f %06f %06f %06f\n" % (classes.index(obj["name"]), center_x, center_y, ww, hh))
    if len(keeps)==0:
        continue
    f=open(labels,"wb")
    for keep in keeps:
        f.write(keep.encode())
    f.flush()
    f.close()
    shutil.copy(jpeg, images)
