import cv2
import mediapipe as mp
import math
import string
import time
import numpy as np

# Inicialização do MediaPipe para detecção de mãos
mp_hands = mp.solutions.hands
hand_detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils


# Funções auxiliares para cálculos e análise
def calculate_dot_product(vector1, vector2):
    dot = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(a ** 2 for a in vector1))
    magnitude2 = math.sqrt(sum(b ** 2 for b in vector2))
    if magnitude1 * magnitude2 == 0:
        return 0
    cos_angle = dot / (magnitude1 * magnitude2)
    angle_degrees = math.degrees(math.acos(min(1.0, max(-1.0, cos_angle))))
    return angle_degrees


def measure_distance_3d(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.z - point2.z) ** 2)


def capture_finger_positions(landmarks):
    finger_states = []
    # Polegar (verificação horizontal)
    if landmarks[4].x < landmarks[3].x:
        finger_states.append(1)  # Estendido
    else:
        finger_states.append(0)  # Fechado

    # Outros dedos (verificação vertical)
    for tip in [8, 12, 16, 20]:
        if landmarks[tip].y < landmarks[tip - 2].y:
            finger_states.append(1)  # Estendido
        else:
            finger_states.append(0)  # Fechado
    return finger_states


def identify_letter(finger_states, landmarks, finger_angle=None):
    letter_dictionary = {
        (1, 0, 0, 0, 0): "A",
        (0, 1, 1, 1, 1): "B",
        (0, 1, 0, 0, 0): "D",
        (1, 1, 1, 0, 0): "K",
        (1, 0, 1, 1, 1): "F",
        (0, 0, 0, 0, 1): "I",
        (0, 1, 0, 0, 1): "H",
        (0, 0, 1, 1, 1): "T",
        (1, 0, 0, 0, 1): "Y",
        (0, 1, 1, 1, 0): "W",
        (1, 1, 1, 1, 0): "N",
        (0, 0, 0, 1, 1): "X",
        (1, 1, 1, 1, 1): "M"
    }

    configuration = tuple(finger_states)

    # Casos especiais onde apenas a posição dos dedos não é suficiente
    if configuration == (0, 0, 0, 0, 0):
        finger_curvature = [measure_distance_3d(landmarks[tip], landmarks[base])
                            for tip, base in zip([4, 8, 12, 16, 20], [2, 5, 9, 13, 17])]
        finger_spacing = (measure_distance_3d(landmarks[8], landmarks[12]) +
                          measure_distance_3d(landmarks[12], landmarks[16]) +
                          measure_distance_3d(landmarks[16], landmarks[20]))
        avg_curvature = sum(finger_curvature) / len(finger_curvature)

        if finger_spacing < 0.07:
            return "O"
        elif avg_curvature < 0.07 and finger_spacing < 0.15:
            return "E"
        elif 0.07 <= avg_curvature <= 0.12 and 0.10 < finger_spacing < 0.25:
            return "S"
        elif 0.07 < finger_spacing < 0.12:
            return "C"

    if configuration == (0, 1, 1, 0, 0):
        index_tip = landmarks[8]
        index_base = landmarks[5]
        middle_tip = landmarks[12]
        middle_base = landmarks[9]

        index_extended = measure_distance_3d(index_tip, index_base) > 0.07
        middle_bent = middle_tip.y > middle_base.y + 0.04
        fingers_aligned = abs(index_tip.x - middle_tip.x) < 0.04

        dist_x = abs(index_tip.x - middle_tip.x)
        dist_y = abs(index_tip.y - middle_tip.y)

        if index_extended and middle_bent and fingers_aligned:
            return "P"
        if dist_x < 0.03 and dist_y < 0.03:
            return "R"
        if finger_angle is not None:
            if finger_angle < 10:
                return "U"
            elif finger_angle > 10:
                return "V"
            else:
                return "?"

    if configuration == (1, 1, 0, 0, 0):
        if finger_angle is not None:
            if finger_angle > 40:
                return "L"
            else:
                return "G"

    return letter_dictionary.get(configuration, "?")


def initial_screen():
    name_input = ""
    while True:
        panel = 255 * np.ones((300, 640, 3), dtype=np.uint8)
        cv2.putText(panel, "Digite seu nome (A-Z) e pressione ENTER", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 0, 0), 2)
        cv2.putText(panel, name_input, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.rectangle(panel, (540, 220), (620, 270), (0, 0, 255), 2)
        cv2.putText(panel, "LIMPAR", (550, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("LibrasVision", panel)
        key = cv2.waitKey(1) & 0xFF

        if key == 13 and name_input:  # ENTER
            cv2.destroyAllWindows()
            return name_input.upper()
        elif key == 8:  # BACKSPACE
            name_input = name_input[:-1]
        elif key == ord('1'):  # 1 para limpar
            name_input = ""
        elif chr(key).upper() in string.ascii_uppercase:
            name_input += chr(key).upper()
        elif key == ord('2'):  # 2 para sair
            cv2.destroyAllWindows()
            exit()


def start_challenge(user_name):
    camera = cv2.VideoCapture(0)
    current_sequence = ""
    current_position = 0
    start_time = time.time()
    challenge_complete = False

    while True:
        success, image = camera.read()
        image = cv2.flip(image, 1)  # Espelhar horizontalmente
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detection_result = hand_detector.process(rgb_image)
        current_letter = "?"

        # Detectar mãos e identificar letras
        if detection_result.multi_hand_landmarks:
            for hand_points in detection_result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_points, mp_hands.HAND_CONNECTIONS)
                finger_positions = capture_finger_positions(hand_points.landmark)

                # Calcular ângulo entre dedos para casos específicos
                angle_between_index_middle = None
                if finger_positions == [0, 1, 1, 0, 0] or finger_positions == [1, 1, 0, 0, 0]:
                    index_vector = (
                        hand_points.landmark[8].x - hand_points.landmark[5].x,
                        hand_points.landmark[8].y - hand_points.landmark[5].y,
                        hand_points.landmark[8].z - hand_points.landmark[5].z
                    )
                    middle_vector = (
                        hand_points.landmark[12].x - hand_points.landmark[9].x,
                        hand_points.landmark[12].y - hand_points.landmark[9].y,
                        hand_points.landmark[12].z - hand_points.landmark[9].z
                    )
                    angle_between_index_middle = calculate_dot_product(index_vector, middle_vector)

                current_letter = identify_letter(finger_positions, hand_points.landmark, angle_between_index_middle)

        # Verificar progresso no desafio
        target_letter = user_name[current_position] if current_position < len(user_name) else ""
        if current_letter == target_letter and not challenge_complete:
            current_sequence += current_letter
            current_position += 1
            if current_position >= len(user_name):
                challenge_complete = True
                final_time = round(time.time() - start_time, 2)
            time.sleep(1)  # Pausa para evitar detecções múltiplas

        if not challenge_complete:
            current_time = round(time.time() - start_time, 2)

        # Interface visual do desafio
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (640, 80), (255, 255, 255), -1)
        alpha = 0.8
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

        cv2.putText(image, f"Meta: {target_letter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)
        cv2.putText(image, f"Progresso: {current_sequence}", (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 0, 100), 2)
        cv2.putText(image, f"Detectado: {current_letter}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 200), 2)

        # Mensagem de conclusão
        if challenge_complete:
            cv2.rectangle(image, (0, 90), (640, 150), (255, 255, 255), -1)
            cv2.putText(image, f"Parabens! Tempo: {final_time}s", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0),
                        3)
            cv2.putText(image, "M: Menu Principal | Q: Sair", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 50, 50), 2)

        cv2.imshow("LibrasVision", image)
        key = cv2.waitKey(1) & 0xFF

        # Tratamento de teclas
        if challenge_complete:
            if key == ord('m'):  # Voltar ao menu
                camera.release()
                cv2.destroyAllWindows()
                start_application()
                return
            elif key == ord('q'):  # Sair
                camera.release()
                cv2.destroyAllWindows()
                exit()

        if key == ord('q'):  # Sair a qualquer momento
            break

    camera.release()
    cv2.destroyAllWindows()


def start_application():
    user_name = initial_screen()
    start_challenge(user_name)


if __name__ == "__main__":
    start_application()