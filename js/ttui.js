class UIBase {
    constructor(params) {
        this.divBg = null;
        this.htmlObj = null;
        this.params = params || {
            text: '...'
        };
    }

    Show() {
        //1.创建div节点
        this.divBg = $T.Create();
        //遮罩
        $T.Attribute(this.divBg, "id", "divBg");
        $T.ClassN(this.divBg, 'graybg');
        $T.Add(this.divBg);
    }

    Close() {
        $T.Del(this.divBg);
    }
}

//create
UIBase.prototype.Create = function (tagname) {
    return document.createElement(tagname || "div");
}

//append
UIBase.prototype.Add = function (el, parent) {
    parent = parent || document.body;
    if (el instanceof UIBase) {
        parent.append(el.htmlObj);
    } else {
        parent.append(el);
    }

}

//Attribute
UIBase.prototype.Attribute = function (e, k, v) {
    e.setAttribute(k, v);
}

//className
UIBase.prototype.ClassN = function (el, classname) {
    if (el instanceof UIBase) {
        el.htmlObj.className += classname + " ";
    } else {
        el.className += classname + " ";
    }

}

//delete
UIBase.prototype.Del = function (el) {
    if (el) {
        let parent1 = el.parentNode;//获取父对象
        parent1.removeChild(el);//通过父对象把它删除
    }
}

UIBase.prototype.Html = function (e, txt) {
    e.innerHTML = txt;
}

UIBase.prototype.Click = function (e, that, cb) {
    e.addEventListener("click", function (ev) {
        ev.preventDefault();
        if (typeof cb == "function") {
            cb.bind(that)();
        } else if (typeof cb == "string") {
            that[cb]();
        }
    }, false);
}

var $T = new UIBase();

//TextBox
class TextBox extends UIBase {
    constructor(params) {
        super(params);
        console.log(params)
        this.Create();
    }

    //创建按钮
    Create() {
        //button
        this.htmlObj = $T.Create();
        $T.ClassN(this.htmlObj, "textbox");
        $T.Html(this.htmlObj, this.params["text"] || "...");
    }
}

//按钮
class Button extends UIBase {
    constructor(params) {
        super(params);
        this.Create();
    }

    //创建按钮
    Create() {
        //button
        this.htmlObj = $T.Create();
        $T.ClassN(this.htmlObj, "button");
        $T.Html(this.htmlObj, this.params["text"] || "but");
        $T.Click(this.htmlObj, this, this.params["click"] || this.btnRun);
    }

    btnRun() {
        console.log("ui button")
    }
}

//画布 image panel
class ImagePanel extends UIBase {
    constructor(params) {
        super(params);
        this.canvas = null;
        this.ctx = null;
        this.width = this.params["width"] || 300;
        this.height = this.params["height"] || 100;
        //创建
        this.Create();
    }

    Create() {
        this.htmlObj = $T.Create("canvas");
        this.canvas = this.htmlObj;
        $T.ClassN(this.canvas, "imagepanel");
        // this.canvas.width = this.width;
        //this.canvas.height = this.height;
        this.ctx = this.canvas.getContext("2d");

        //this.DrawL();
    }

    //测试绘制直线
    DrawL() {
        this.ctx.save(); //保存状态
        this.ctx.beginPath();
        this.ctx.lineWidth = 2;
        this.ctx.strokeStyle = "red";
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(this.canvas.width, this.canvas.height);
        this.ctx.stroke();

        this.ctx.restore(); //恢复画布状态
    }
    //绘制图片
    DrawImage(img0) {
        let that = this;
        let imgObj = new Image();
        imgObj.src = img0;
        imgObj.onload = function () {
            that.ctx.drawImage(imgObj, 0, 0);
        }
    }
    //复制来自其它canvas.ctx的区域
    DrawImageData(imgData0) {
        //putImageData用于将图像数据重写至Canvas画布
        this.ctx.putImageData(imgData0, 0, 0);
    }

    GetPNG() {
        return this.canvas.toDataURL("image/png");
    }


}
//对话框
class Dialog extends UIBase {
    constructor(params) {
        super(params);
        this.divForm = null;
    }

    //创建对话框
    Show() {
        super.Show();
        //2.创建对话框
        this.divForm = $T.Create();
        //对话框
        $T.Attribute(this.divForm, "id", 'dlgForm');
        $T.ClassN(this.divForm, 'form');
        //title
        let divTitle = $T.Create();
        $T.ClassN(divTitle, "title");
        $T.Html(divTitle, "标题");
        $T.Add(divTitle, this.divForm);
        //关闭按钮
        let btnClose = $T.Create();
        $T.ClassN(btnClose, 'close');
        $T.Html(btnClose, 'X');
        $T.Click(btnClose, this, "Close");
        $T.Add(btnClose, divTitle);
        //content
        if (this.params['content'] instanceof UIBase) {
            $T.ClassN(this.params['content'], "content");
            $T.Add(this.params['content'], this.divForm);
        } else {
            let tb1 = new TextBox({ text: this.params['text'] || "上传中..." });
            $T.ClassN(tb1, "content");
            $T.Add(tb1, this.divForm);
        }
        // let panel1 = new ImagePanel();
        // $T.ClassN(panel1,"content");
        // $T.Add(panel1, this.divForm);

        //buttons
        let divButtons = $T.Create();
        $T.ClassN(divButtons, "buttons");
        $T.Add(divButtons, this.divForm);
        //ok button
        let butOk = new Button({
            text: 'Ok', click: (e) => {
                //闭包的作用 传递 this
                this.btnOk();
            }
        });
        $T.Add(butOk, divButtons);
        //cancel button
        let butCancel = new Button({
            text: 'Cancel', click: (e) => {
                this.btnCancel();
            }
        });
        $T.Add(butCancel, divButtons);
        //添加
        $T.Add(this.divForm);
    }

    Close() {
        super.Close();
        $T.Del(this.divForm);
    }

    btnOk() {
        this.Close();
    }

    btnCancel() {
        this.Close();
    }
}

//提示
class Toast extends UIBase {
    constructor(params) {
        super(params);
        this.divForm = null;
    }

    //创建对话框
    Show() {
        super.Show();
        //2.创建对话框
        this.divForm = $T.Create('div');
        //对话框
        $T.Attribute(this.divForm, "id", 'dlgForm');
        $T.ClassN(this.divForm, 'form');
        $T.Html(this.divForm, this.params['text']);
        this.divForm.style.height = "100px";
        this.divForm.style.width = "100px";
        //添加
        $T.Add(this.divForm);
    }

    Close() {
        super.Close();
        $T.Del(this.divForm);

    }
}

