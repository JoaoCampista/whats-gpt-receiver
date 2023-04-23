
from openai_api import *

token = os.environ["WHATSAPP_TOKEN"]

def get_whatsapp_mesage(body):

    if body.get("object") and body.get("entry"):
        entry = body["entry"][0]
        if entry.get("changes"):
            value = entry["changes"][0]["value"]
            if value.get("messages"):

                phone_number_id = value["metadata"]["phone_number_id"]
                from_number = value["messages"][0]["from"]
                from_name = value["contacts"][0]["profile"]
                msg_body = value["messages"][0]["text"]["body"]
                
                url = f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={token}"

                print(from_number)
                print(msg_body)
                
                intention = classify_text(msg_body)
                print(intention)

                if intention == 'Criar uma imagem':
                    dalle_msg = dalle_return(msg_body)
                    print(dalle_msg)

                    data = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": from_number,
                        "type": "image",
                        "image": {
                            "link": dalle_msg
                        }
                    } 

                elif intention == 'Responder uma pergunta':
                    prompt = (f"{msg_body}. Me responda apenas em português e de forma efetiva e direta")
                    gpt_msg = gpt_return(prompt)
                    print(gpt_msg)

                    data = {
                        "messaging_product": "whatsapp",    
                        "recipient_type": "individual",
                        "to": from_number,
                        "type": "text",
                        "text": {
                            "preview_url": False,
                            "body": gpt_msg
                        }
                    }
                
                headers = { "Content-Type": "application/json" }
                
                #requests.post(url, json=data, headers=headers)

                return data