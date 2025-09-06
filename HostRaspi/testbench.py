import nlp

color_queue = []
arm_queue = []
action_queue = []

items = ["pme","teo","teeere"]

for it,i in enumerate(items):
    print(f"item: {it}, index: {i}")

#nlp.record_audio()
#transcribed_text = nlp.transcribe_audio()
transcribed_text = "pick up color red arm one then pick up arm two then pick up arm one color blue then pick up then".split(" ")     
print(f"You said: \"{transcribed_text}\" and length is {len(transcribed_text)}")
i = 0
while i < len(transcribed_text):
    # Check the action
    if transcribed_text[i] == "pick" and i+1 < len(transcribed_text):
        if transcribed_text[i+1] == "up":
            print("Pick up action triggered!")
            action_queue.append("p")
            i += 2
            arm_queue.append("x")
            color_queue.append("x")
            while i+1 < len(transcribed_text):
                print(transcribed_text[i])
                if transcribed_text[i] == "then" or transcribed_text[i] == None:
                    break
                elif transcribed_text[i] == "arm":
                    if transcribed_text[i+1] == "one" or transcribed_text[i+1] == "two" or transcribed_text[i+1] == "too":
                        print(f"choosing arm, {transcribed_text[i+1]}")
                        arm_queue.pop()
                        arm_queue.append(transcribed_text[i+1])
                        i += 2
                        continue
                    i+=1
                    continue
                elif transcribed_text[i] == "color":
                    if transcribed_text[i+1] == "red" or transcribed_text[i+1] == "green" or transcribed_text[i+1] == "blue":
                        print(f"choosing color, {transcribed_text[i+1]}")
                        color_queue.pop()
                        color_queue.append(transcribed_text[i+1])
                        i += 2
                        continue
                    i+=1
                    continue                    
                else:
                    i+=1
                continue
    i += 1


k = 0
print("while loop starting...") 
while k < len(action_queue):
    print(f"index: {k} | color: {color_queue[k]} | arm: {arm_queue[k]} | action: {action_queue[k]}")
    k += 1