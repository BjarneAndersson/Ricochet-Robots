# ----------STRING----------
msg: str = "Ricochet Robots"
msg_encoded: bytes = \
    str(msg).encode(encoding='utf-8')
msg_decoded: str = \
    msg_encoded.decode(encoding='utf-8')

# ----------OBJECT----------
import pickle

msg: dict = {
    'first_name': 'Bjarne',
    'last_name': 'Andersson'
}
msg_pickled: bytes = pickle.dumps(msg)
msg_obj: dict = pickle.loads(msg_pickled)
