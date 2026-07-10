# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from TEAMZYRO import collection, app, user_collection, require_power
from TEAMZYRO.unit.zyro_rarity import rarity_map

@app.on_message(filters.command("gdelete"))
@require_power("del")
async def delete_handler(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("Incorrect format... Please use: /gdelete ID")
            return

        character_id = args[1]

        character = await collection.find_one_and_delete({'id': character_id})
        if character:
            update_result = await user_collection.update_many(
                {'characters.id': character_id},
                {'$pull': {'characters': {'id': character_id}}}
            )
            await message.reply_text(
                f"Character with ID {character_id} deleted successfully from the database.\n"
                f"Removed from {update_result.modified_count} user collections."
            )
        else:
            await message.reply_text(f"Character with ID {character_id} not found in the database.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@app.on_message(filters.command("gupdate"))
@require_power("up")
async def update(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 4:
            await message.reply_text('Incorrect format. Please use: /gupdate id field new_value')
            return

        character_id = args[1]
        field_to_update = args[2]
        # यहाँ पूूरा न्यू वैल्यू कैप्चर करने के लिए जॉइन किया गया है
        new_value = " ".join(args[3:]).strip()

        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if field_to_update not in valid_fields:
            await message.reply_text(f'Invalid field. Please use one of the following: {", ".join(valid_fields)}')
            return

        if field_to_update in ['name', 'anime']:
            new_value = new_value.replace('-', ' ').title()
        elif field_to_update == 'rarity':
            try:
                new_value = rarity_map[int(new_value)]
            except (KeyError, ValueError):
                await message.reply_text('Invalid rarity. Please use a valid number between 1-12 for rarity.')
                return

        result = await collection.update_one({'id': character_id}, {'$set': {field_to_update: new_value}})
        if result.modified_count == 0:
            await message.reply_text('Character not found or no changes made.')
            return

        total_users = await user_collection.count_documents({'characters.id': character_id})
        if total_users == 0:
            await message.reply_text('sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘᴅᴀᴛᴇ ✅')
            return

        progress_message = await message.reply_text('Updating users: 0% completed...')
        
        # इंडिविजुअल लूप की जगह सीधा update_many का उपयोग परफॉर्मेंस बढ़ाएगा
        update_res = await user_collection.update_many(
            {'characters.id': character_id},
            {'$set': {f'characters.$.{field_to_update}': new_value}}
        )

        await progress_message.edit_text('Updating: 100% completed.')
        await message.reply_text(f'sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘᴅᴀᴛᴇ ✅ \nTotal users updated: {update_res.modified_count}/{total_users}')

    except Exception as e:
        await message.reply_text(f'Error: {str(e)}')

@app.on_message(filters.command("maxupdate"))
@require_power("up")
async def update_multiple(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 4:
            await message.reply_text('Incorrect format. Use: /maxupdate id1,id2,id3 field new_value')
            return

        character_ids = args[1].split(',')
        field_to_update = args[2]
        new_value = ' '.join(args[3:]).strip()

        valid_fields = ['img_url', 'vid_url', 'name', 'anime', 'rarity']
        if field_to_update not in valid_fields:
            await message.reply_text(f'Invalid field. Use one of: {", ".join(valid_fields)}')
            return

        if field_to_update in ['name', 'anime']:
            new_value = new_value.replace('-', ' ').title()
        elif field_to_update == 'rarity':
            try:
                new_value = rarity_map[int(new_value)]
            except (KeyError, ValueError):
                await message.reply_text('Invalid rarity. Use a valid number between 1-12 for rarity.')
                return

        total_characters = len(character_ids)
        updated_characters = 0
        total_users_updated = 0

        progress_message = await message.reply_text('Updating multiple characters: 0% completed...')
        next_progress_update = 10

        for i, character_id in enumerate(character_ids, start=1):
            result = await collection.update_one({'id': character_id}, {'$set': {field_to_update: new_value}})
            if result.modified_count == 0:
                continue

            # यहाँ पर भी परफॉर्मेंस बूस्ट के लिए update_many यूज़ किया गया है
            user_res = await user_collection.update_many(
                {'characters.id': character_id},
                {'$set': {f'characters.$.{field_to_update}': new_value}}
            )
            total_users_updated += user_res.modified_count
            updated_characters += 1

            progress = (i / total_characters) * 100
            if progress >= next_progress_update:
                await progress_message.edit_text(f'Updating: {int(progress)}% completed...')
                next_progress_update += 10
                await asyncio.sleep(1) # यहाँ non-blocking sleep लगाया गया है

        await progress_message.edit_text('Updating: 100% completed.')
        await message.reply_text(
            f'sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘᴅᴀᴛᴇ ✅ \nTotal characters updated: {updated_characters}/{total_characters}. '
            f'Total users updated: {total_users_updated}.'
        )

    except Exception as e:
        await message.reply_text(f'Error: {str(e)}')
