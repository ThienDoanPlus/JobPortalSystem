from JobPortalSystem_app import create_app
# Dùng để chạy app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, port=2004)