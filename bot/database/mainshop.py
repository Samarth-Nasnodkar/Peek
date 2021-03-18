from models.item import Item

# shop = [
#     {
#         "name": "watch",
#         "emoji": ":stopwatch:",
#         "price": 100
#     },
#     {
#         "name": "phone",
#         "emoji": ":mobile_phone:",
#         "price": 1000
#     },
#     {
#         "name": "dragon",
#         "emoji": ":dragon_face:",
#         "price": 100000
#     }
# ]

shop = [
    Item("watch", ":stopwatch:", price=100),
    Item("phone", ':mobile_phone:', price=1000),
    Item("dragon", ":dragon_face:", price=100000)
]
