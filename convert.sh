PYTHONPATH=. python3 models/export.py --weights runs/exp0/weights/best.pt 
python3 -m onnxsim runs/exp0/weights/best.onnx yolov5s.onnx
