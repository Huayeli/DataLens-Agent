let chart=null;


// 当前数据集
let currentDataset=null;



// ===============================
// 初始化
// ===============================

window.onload=function(){


    loadDatasets();


    let input=document.getElementById("msg");


    if(input){

        input.addEventListener(
            "keydown",
            function(e){

                if(e.key==="Enter"){

                    e.preventDefault();

                    sendMsg();

                }

            }
        );

    }

};




// ===============================
// 发送消息
// ===============================

async function sendMsg(){


    let input=document.getElementById("msg");


    let msg=input.value.trim();



    if(!msg)
        return;



    // 保留用户输入
    addMessage(
        "user",
        msg
    );



    input.value="";



    let loading=addMessage(
        "ai",
        "正在分析数据..."
    );



    try{


        let res=await fetch(

            "http://127.0.0.1:8000/chat",

            {

                method:"POST",

                headers:{

                    "Content-Type":
                    "application/json"

                },


                body:JSON.stringify({

                    message:msg,

                    dataset:currentDataset

                })

            }

        );



        let data=await res.json();



        removeMessage(loading);



        addMessage(

            "ai",

            data.answer ||
            "暂无分析结果"

        );



        showSQL(
            data.sql
        );


        showTable(
            data.data
        );


        drawChart(

            data.data,

            data.chart,

            data.x,

            data.y

        );



    }


    catch(e){


        removeMessage(loading);


        addMessage(

            "ai",

            "请求错误："+e.message

        );


    }


}







// ===============================
// 添加聊天
// ===============================

function addMessage(type,text){


    let box=document.getElementById(
        "chatBox"
    );


    let div=document.createElement(
        "div"
    );


    div.id=
    "msg_"+
    Date.now()+
    Math.random();



    div.className=
    type==="user"
    ?
    "user bubble"
    :
    "ai bubble";



    text=text
    .replace(/\*\*(.*?)\*\*/g,"$1")
    .replace(/\n/g,"<br>");



    div.innerHTML=text;



    box.appendChild(div);



    box.scrollTop=
    box.scrollHeight;



    return div;

}





function removeMessage(el){


    if(el){

        el.remove();

    }

}







// ===============================
// SQL显示
// ===============================

function showSQL(sql){


    let box=document.getElementById(
        "sqlBox"
    );


    if(box){

        box.innerText=
        sql ||
        "暂无SQL";

    }

}







// ===============================
// 数据表格
// ===============================

function showTable(data){


    let box=document.getElementById(
        "tableBox"
    );


    if(!box)
        return;



    if(!data || data.length===0){

        box.innerHTML=
        "暂无数据";

        return;

    }



    let keys=
    Object.keys(
        data[0]
    );



    let html="<table>";



    html+="<tr>";



    keys.forEach(k=>{


        html+=
        `<th>${k}</th>`;


    });



    html+="</tr>";





    data.forEach(row=>{


        html+="<tr>";



        keys.forEach(k=>{


            html+=
            `<td>${row[k]}</td>`;


        });



        html+="</tr>";


    });



    html+="</table>";



    box.innerHTML=html;


}







// ===============================
// Echarts
// ===============================

function drawChart(
    data,
    type,
    x,
    y
){


    if(!data || data.length===0)
        return;



    let dom=document.getElementById(
        "chart"
    );



    if(!dom)
        return;



    if(chart)
        chart.dispose();



    chart=echarts.init(dom);



    let keys=
    Object.keys(
        data[0]
    );



    x=x || keys[0];

    y=y || keys[1];



    let option={


        tooltip:{

            trigger:"axis"

        },



        grid:{

            containLabel:true

        },



        xAxis:{


            type:"category",


            data:
            data.map(
                item=>item[x]
            )


        },



        yAxis:{


            type:"value"


        },



        series:[{


            name:y,


            type:
            type==="line"
            ?
            "line"
            :
            "bar",



            data:
            data.map(
                item=>
                Number(item[y])
            ),


            label:{


                show:true


            }


        }]


    };



    chart.setOption(option);



    window.onresize=function(){

        chart.resize();

    };


}







// ===============================
// 上传CSV
// ===============================

function selectCSV(){


    document
    .getElementById(
        "csvFile"
    )
    .click();


}






async function uploadCSV(){


    let file=document
    .getElementById(
        "csvFile"
    )
    .files[0];



    if(!file)
        return;



    let form=new FormData();



    form.append(
        "file",
        file
    );



    let res=await fetch(

        "http://127.0.0.1:8000/upload",

        {

            method:"POST",

            body:form

        }

    );



    let data=await res.json();



    alert(
        data.message ||
        "上传成功"
    );



    currentDataset=data.table;



    loadDatasets();


}







// ===============================
// 加载数据集
// ===============================

async function loadDatasets(){


    let box=document.getElementById(
        "datasetList"
    );


    if(!box)
        return;



    let res=await fetch(

        "http://127.0.0.1:8000/datasets"

    );



    let data=await res.json();



    box.innerHTML="";



    data.datasets.forEach(item=>{


        let div=document.createElement(
            "div"
        );



        div.className=
        "dataset-card";



        div.innerHTML=

        `
        📁 ${item}
        `;




        if(item===data.current){


            currentDataset=item;


            div.classList.add(
                "active"
            );


        }





        div.onclick=function(){


            switchDataset(item);


        };



        box.appendChild(div);


    });


}







// ===============================
// 切换数据集
// ===============================

async function switchDataset(name){


    let res=await fetch(


        "http://127.0.0.1:8000/switch/"+name,


        {

            method:"POST"

        }


    );



    let data=await res.json();




    if(data.success){


        currentDataset=name;



        loadDatasets();



        addMessage(

            "ai",

            "当前已切换数据集："+name

        );


    }


}