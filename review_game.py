async def pick_random_student(app, chat_id):
    members = []
    async for member in app.get_chat_members(chat_id):
        if not member.user.is_bot:
            members.append(member.user.first_name)
    if members:
        import random
        return random.choice(members)
    return None
