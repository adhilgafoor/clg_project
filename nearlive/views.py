if user.is_superuser:
    messages.success(request, "Admin logged in successfully.")
    return redirect('/adminhome')
