# import base64
# from io import BytesIO
from flask import Flask, send_file, jsonify, request
from matplotlib.figure import Figure
import io
import base64
import pydicom
import numpy as np
from PIL import Image
import cv2

app = Flask(__name__)

@app.route("/load_image_file")
def load_image_file():
    # Image File을 Flutter App으로 전송
    return send_file("./Data/image.png", mimetype="image/png")


@app.route("/make_image_file")
def make_image_file():
    # Flask에서 이미지를 생성할때는 pyplot을 사용하면 안된다.
    fig = Figure()
    ax = fig.subplots()

    ax.plot([1, 2, 3, 4], [10, 20, 30, 40])
    fig.savefig("./Data/image1.png")
    # Image File을 Flutter App으로 전송
    return send_file("./Data/image1.png", mimetype="image/png")

@app.route("/base64_image_file")
def base64_image_file():
    # Flask에서 이미지를 생성할때는 pyplot을 사용하면 안된다.
    fig = Figure()
    ax = fig.subplots()

    ax.plot([1, 2, 3, 4], [100, 20, 50, 3])
    buffer = io.BytesIO()
    fig.savefig(buffer, format = 'png')
    buffer.seek(0)
    # 이미지를 Base64로 Encoding
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')    
    # print(image_base64)
    # Image File을 Flutter App으로 전송
    return jsonify({'result' : image_base64})

@app.route("/base64_dcm_file")
def base64_dcm_file():
    # Flask에서 이미지를 생성할때는 pyplot을 사용하면 안된다.
    filename = "./Data/0002.DCM"
    dcm = pydicom.dcmread(filename)
    new_image = dcm.pixel_array.astype(float)
    scaled_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0
    scaled_image = np.uint8(scaled_image)
    final_image = Image.fromarray(scaled_image[0])

    buffer = io.BytesIO()
    final_image.save(buffer, format = 'png')

    buffer.seek(0)
    # 이미지를 Base64로 Encoding
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return jsonify({'result' : image_base64})

# @app.route("/base64_dcm_window_file")
# def base64_dcm_window_file():
#     windowCenter = float(request.args.get('wc'))
#     windowWidth = float(request.args.get('ww'))
#     filename = "./Data/CR.1.2.410.200013.1.510.1.20210310170346701.0009.dcm"
    
#     # Print the windowCenter and windowWidth values
#     print(f"Received Window Center: {windowCenter}")
#     print(f"Received Window Width: {windowWidth}")

#     # Now let's print the values from the DICOM file
#     dcm = pydicom.dcmread(filename)
#     print(f"Actual Window Center: {dcm.WindowCenter}")
#     print(f"Actual Window Width: {dcm.WindowWidth}")

#     convert_file(filename, filename + ".png", windowCenter, windowWidth)
#     with open(filename + ".png", 'rb') as img:
#         image_base64 = base64.b64encode(img.read()).decode('utf-8')
#     return jsonify({
#         'result': image_base64,
#         'windowCenter': dcm.WindowCenter,
#         'windowWidth': dcm.WindowWidth,
#         })

# def convert_file(dcm_file_path, png_file_path, x, y):
#     dcm = pydicom.dcmread(dcm_file_path)
#     img = dcm.pixel_array.astype(float)
#     scaled_image = cv2.convertScaleAbs(img - dcm.WindowCenter + x, alpha=(255.0 / dcm.WindowWidth) + y)   
#     cv2.imwrite(png_file_path, scaled_image)
@app.route("/base64_dcm_window_file")
def base64_dcm_window_file():
    windowCenter = float(request.args.get('wc'))
    windowWidth = float(request.args.get('ww'))
    filename = "./Data/CR.1.2.410.200013.1.510.1.20210310170346701.0009.dcm"
    
    # Print the windowCenter and windowWidth values
    print(f"Received Window Center: {windowCenter}")
    print(f"Received Window Width: {windowWidth}")

    # Now let's print the values from the DICOM file
    dcm = pydicom.dcmread(filename)
    print(f"Actual Window Center: {dcm.WindowCenter}")
    print(f"Actual Window Width: {dcm.WindowWidth}")

    # Print the range of windowCenter and windowWidth
    min_window_center = dcm.WindowCenter - dcm.WindowWidth / 2.0
    max_window_center = dcm.WindowCenter + dcm.WindowWidth / 2.0
    min_window_width = 0.1  # Assuming a minimum value for window width
    max_window_width = dcm.WindowWidth * 2  # Adjust the multiplier as needed

    print(f"Range of Window Center: {min_window_center} to {max_window_center}")
    print(f"Range of Window Width: {min_window_width} to {max_window_width}")


    generate_png_files(
        base_filename=filename,
        window_center_range=(min_window_center, max_window_center),
        window_width=dcm.WindowWidth
    )


    convert_file(filename, filename + ".png", windowCenter, windowWidth)
    with open(filename + ".png", 'rb') as img:
        image_base64 = base64.b64encode(img.read()).decode('utf-8')
    
    return jsonify({
        'result': image_base64,
        'windowCenter': dcm.WindowCenter,
        'windowWidth': dcm.WindowWidth,
        })
        
    
def generate_png_files(base_filename, window_center_range, window_width):
    for i in range(50):
        start_value = window_center_range[0]
        end_value = window_center_range[1]
        step = (end_value - start_value) / 50.0
        window_center = start_value + i * step
        convert_file(f"./TestPng/{base_filename}_img_{i}.png", window_center, window_width)



def convert_file(dcm_file_path, png_file_path, x, y):
    dcm = pydicom.dcmread(dcm_file_path)
    img = dcm.pixel_array.astype(float)
    scaled_image = cv2.convertScaleAbs(img - dcm.WindowCenter + x, alpha=(255.0 / dcm.WindowWidth) + y)   
    cv2.imwrite(png_file_path, scaled_image)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True, threaded=True)
