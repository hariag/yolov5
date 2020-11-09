export PYTHONPATH="$PWD" && python3 models/export.py --weights runs/exp8/weights/best.pt --img 320 --batch 1
python3 -m onnxsim runs/exp8/weights/best.onnx yolov5s-simplified.onnx
/home/haria/ncnn/build/tools/onnx/onnx2ncnn yolov5s-simplified.onnx
