import cv2

def convert_video_to_images(path, frame_count = -1):
    frames = []

    cap = cv2.VideoCapture(filename=path)
    count = 0

    success = True
    frame_counter = 0

    while success:
        success, frame = cap.read()

        if not success:
            break

        count += 1
        encode_success, image = cv2.imencode(".png", frame)

        if not encode_success:
            raise Exception("Failed to encode frame")

        frames.append(image)
        frame_counter += 1
        print(f"Processed Video Frame: {frame_counter}")

        if frame_count > 0 and frame_counter == frame_count:
            break

    cap.release()
    cv2.destroyAllWindows()
    return frames