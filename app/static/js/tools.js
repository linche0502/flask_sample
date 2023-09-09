




const thisUrl = `${location.protocol}//${location.host}${location.pathname}`;
const weekdayTranslate= {"0":"週日", "1":"週一", "2":"週二", "3":"週三", "4":"週四", "5":"週五", "6":"週六"}
const onDOMContentLoaded = function onDOMContentLoaded(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    };

    
function toSBC(str) {
    var result = "";
    for (i=0; i<str.length; i++) {
        var cCode = str.charCodeAt(i);
        //全形與半形相差 (除空格外): 0xFEE0 (65248 十進位制)
        if (cCode>=0xFF01 && cCode<=0xFF5E){
            cCode-= 65248;
            //cCode = (cCode >= 0xFF01 && cCode <= 0xFF5E) ? (cCode - 65248) : cCode;
        }
        //處理空格
        if (cCode == 0x00300){
            cCode= 0x0020;
            //cCode = (cCode == 0x03000) ? 0x0020 : cCode;
        }
        result += String.fromCharCode(cCode);
    }
    return result;
}


function strWidth(str){
    var count= 0;
    for(var i=0; i<str.length; i++){
        if (str.charCodeAt(i)>65248 || str.charCodeAt(i)==12288){
            count+= 2;
        }
        else{
            count+= 1;
        }
    }
    return (str.match(/[\x00-\xff]/g) || '').length+
        (str.match(/[^\x00-\xff]/g) || '').length*2
}


function strikeThrough(text, add) {
    if(add){
        return text.split('').map(char => char + '\u0336').join('')
    }
    else{
        return text.replace(/[\u0336]/g, '')
    }
}


function getDate(args= {}){
    var nowDate= new Date();
    nowDate = new Date(
        nowDate.getFullYear()+ (args["yearDelta"]||0),
        nowDate.getMonth()+(args["monthDelta"]||0),
        nowDate.getDate()+(args["dateDelta"]||0)
    );
    return String(nowDate.getFullYear()).padStart(4, '0')+
        "-"+ String((nowDate.getMonth()+ 1)).padStart(2, '0')+
        "-"+ String(nowDate.getDate()).padStart(2, '0');
    // `${String(nowDate.getFullYear()).padStart(4,'0')}-${String((nowDate.getMonth()+1)).padStart(2,'0')}-${String(nowDate.getDate()).padStart(2,'0')}`
}

// input[type='radio'][data-radio-cancelable] 再點擊一次取消取
let inputRadioValue= {};
onDOMContentLoaded(() => {
    document.querySelectorAll("input[type='radio'][data-radio-cancelable]").forEach(e => {
        e.addEventListener("click", () => {
            if(inputRadioValue[e.name] == e.value){
                e.checked= false;
                inputRadioValue[e.name]= null;
                e.blur();
            }
            else{
                inputRadioValue[e.name]= e.value;
            }
        });
    });
});

// <input type='number'> 的加減按鈕
document.addEventListener("DOMContentLoaded", () => {
    var inputBtnTypes= ["btn-minus","btn-plus"];
    inputBtnTypes.forEach(inputBtnType => {
        // 為每一個.btn-minus/btn-plus新增一個onclick事件
        document.querySelectorAll('.'+inputBtnType).forEach(e => {
            e.onclick= () => {
                if(inputBtnType=="btn-minus"){
                    // 對同階層的input[type='number']做加減
                    e.parentElement.querySelector("input[type='number']").stepDown();
                }
                else if(inputBtnType=="btn-plus"){
                    e.parentElement.querySelector("input[type='number']").stepUp();
                }
                
            };
        });
    });
});

function getUrlParams(paramName=null){
    var url = new URL(window.location.href);
    if(paramName){
        return url.searchParams.get(paramName);
    }
    else{
        var paramsDict= {};
        for(var [key, value] of url.entries()){
            paramsDict[key]= value;
        }
        return paramsDict;
    }
}

function setUrlParams(paramName={}){
    var url = new URL(window.location.href);
    if(paramName){
        return url.searchParams.get(paramName);
    }
    else{
        var paramsDict= {};
        for(var [key, value] of url.entries()){
            paramsDict[key]= value;
        }
        return paramsDict;
    }
}

function getCookie(name=null, {specChar=false}={}){
    var cookieObj= {};
    var tempCookie;
    document.cookie.split(';').forEach(cookie => {
        tempCookie= cookie.split('=');
        cookieObj[tempCookie[0].trim()] = tempCookie[1];
    });
    if(name){
        return (specChar && cookieObj[name]!=undefined)? cookieObj[name].replace(/；/g,';').replace(/　/g,' ').replace(/，/g,',') : cookieObj[name]
    }
    else{
        return cookieObj;
    }
}

function setCookie(name, value, {path=location.pathname, expireDay=null, specChar=false}={}){
    var valueStr= (specChar)? value.replace(/;/g,'；').replace(/ /g,'　').replace(/,/g,'，') : value;
    expireDay= (expireDay)? new Date(expireDay).toGMTString() : "Fri, 31 Dec 9999 23:59:59 GMT";
    var cookieStr= `${name}=${valueStr}; path=${path}; expires=${expireDay};`
    if(new Blob([cookieStr]).size > 4000){
        throw(`cookie out of size ${new Blob([cookieStr]).size}/4000 bytes`);
    }
    document.cookie= cookieStr;
}

// 確認是否為inWebApp 而不是一般瀏覽器
function isWebview() {
    var useragent = navigator.userAgent;
    var rules = ['WebView', '(iPhone|iPod|iPad)(?!.*Safari\/)', 'Android.*(wv|\.0\.0\.0)'];
    var regex = new RegExp(`(${rules.join('|')})`, 'ig');
    return Boolean(useragent.match(regex));
}

// 防止螢幕進入睡眠
function noSleep(autoStart=true){
    return new Promise((resolve,reject) => {
        var script= document.createElement("script");
        document.querySelector("head").appendChild(script);
        script.onload= function(){
            var noSleep= new NoSleep();
            if(autoStart){ noSleep.enable(); };
            resolve(noSleep);
        };
        script.src= "https://richtr.github.io/NoSleep.js/dist/NoSleep.min.js";
    })
}

// 在沒有state加密的情況下
function decodeJWT(text){
    var base64Url = text.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    
    return decodeURIComponent(
        window.atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join('')
    )
}
