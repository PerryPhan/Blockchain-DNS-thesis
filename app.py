from flask import Flask, render_template, url_for, request, session, redirect, jsonify

app = Flask(__name__)
'''
  TODO: Tạo simple form -> Insert record từ form ( một hoặc nhiều ) -> xử lý cho ra dữ liệu khi nhận route 
  TODO: Tạo CSDL dạng Blockchain để lưu trữ records & blockchain gắn cái blocks từ CSDL 
  TODO: Tạo route để phân giải
'''
@app.route('/')
def index():
    return redirect('/dns/form')

@app.route('/dns/form', methods=['POST','GET'])
def form():
    if request.method == 'POST':
        return jsonify(request.form)
    return render_template('index.html')

@app.route('/blockchain/load')
def loadBlockchain():
    return "Hi doin?"

@app.route('/dns/resolve')
def resolve():
    return "Hi"

if __name__ == "__main__":
    app.run()
