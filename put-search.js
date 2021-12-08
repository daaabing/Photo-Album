window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const synth = window.speechSynthesis;
const recognition = new SpeechRecognition();

$(document).ready(() => {
    $(".img-display")[0].style.display = "none"
    // AWS.config.region = 'us-east-1';
    // AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    //     IdentityPoolId: 'us-east-1:df85fdb0-b8bd-492e-bb6e-c09eebc615c5',
    // });
    $("#stop")[0].style.display = "none"
})


var filename1 = '';
var encoded = null;
var fileExt = null;

function previewFile(input) {
    var reader = new FileReader();
    filename1 = input.files[0].name;
    fileExt = filename1.split(".").pop();
    var onlyname = filename1.replace(/\.[^/.]+$/, "");
    var finalName = onlyname + "_" + Date.now() + "." + fileExt;
    filename1 = finalName;
  
    reader.onload = function (e) {
      var src = e.target.result;
      var newImage = document.createElement("img");
      newImage.src = src;
      encoded = newImage.outerHTML;
    }
    reader.readAsDataURL(input.files[0]);
  }

function uploadPhoto() {
    last_index_quote = encoded.lastIndexOf('"');
    if (fileExt == 'jpg' || fileExt == 'jpeg') {
        encodedStr = encoded.substring(33, last_index_quote);
    }
    else {
        encodedStr = encoded.substring(32, last_index_quote);
    }
    let customLabels = prompt("Give tags to your photo (speraterd by comma):", "");

    let params = {
        key: filename1,
        bucket: "hw2-b2-123",
        "x-amz-meta-customLabels": customLabels,
        // "x-api-key": "ruGrf0a6IG6FZQFKW4wN73evJ9x4lJmCaXbEC9uG", 
        "Content-Type": "image/jpeg;base64"
    };
    buf = encodedStr;
    let body = buf;
    let additionalParams = {
        headers: {
            "x-amz-meta-customLabels": customLabels,
            // "x-api-key": "ruGrf0a6IG6FZQFKW4wN73evJ9x4lJmCaXbEC9uG",
            "Content-Type": "image/jpeg;base64"
        }
    };

    console.log(params)

    sdk.uploadBucketKeyPut(params, body, additionalParams)
        .then(result => {
            console.log('success OK');
            console.log(result);
            alert("Photo uploaded successfully!");
        }).catch(result => {
            console.log(result);
        });
}


function searchPhotos() {
    let params = {
        "q":$('#query_string')[0].value,
        // "x-api-key": "ruGrf0a6IG6FZQFKW4wN73evJ9x4lJmCaXbEC9uG"
    }
    $(".img-display").empty()
    console.log(params)
    sdk.searchGet(params, {}, {}).then(
        res => {
            if (res["data"].length > 0) {
                res["data"].forEach(img_path => {
                    let img = new Image();
                    img.src = "https://hw2-b2-123.s3.us-east-2.amazonaws.com/" + img_path;
                    img.setAttribute("class", "banner-img");
                    img.setAttribute("alt", "effy");
                    $(".img-display")[0].appendChild(img);
                });
                $(".img-display")[0].style.display = "block"
            }
        }).catch(result => {console.log("label not detected by lex.")})    
}

function searchFromVoiceStart() {
    recognition.start();
    document.getElementById("stop").style.display = "block";
    document.getElementById("record").style.display = "none";
}

function searchFromVoiceEnd() {
    var result = recognition.stop();
    document.getElementById("record").style.display = "block"
    document.getElementById("stop").style.display = "none"
    recognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        console.log(speechToText)
    
        document.getElementById('query_string').value = speechToText;
    }
}
