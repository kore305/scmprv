@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")

        # User bubble
        user_html = f"""
        <div class="flex justify-end mb-2">
            <div class="bg-green-600 text-white p-3 rounded-2xl max-w-xs shadow text-sm">
                {user_message}
            </div>
        </div>
        """

        # DB search
        programs = search_programs_in_db(user_message)
        db_reply = ""
        if programs.exists():
            db_reply += "<p class='font-semibold mb-1'>✅ Related programs:</p>"
            for p in programs:
                db_reply += f"<div class='mb-2 text-sm'><strong>{p.name}</strong> ({p.agency})<br>{p.description}</div>"
        else:
            db_reply = "<p class='text-gray-600 text-sm'>ℹ️ No direct matches in the database.</p>"

        # AI reply
        ai_reply = query_openrouter(user_message)

        # Bot bubble
        bot_html = f"""
        <div class="flex justify-start mb-4">
            <div class="bg-gray-200 text-gray-900 p-3 rounded-2xl max-w-xs shadow text-sm">
                {db_reply}
                <div class="mt-2 text-gray-800">{ai_reply}</div>
            </div>
        </div>
        """

        return HttpResponse(user_html + bot_html)

    return render(request, "website/chatbot.html")