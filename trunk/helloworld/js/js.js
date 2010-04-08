function sayHello(){
    var myVariable = 'Hello';
    window.alert(myVariable);
}

function getDetails(obj){
    clickX = window.event.x-obj.offsetLeft;
    clickY = window.event.y-obj.offsetTop;
    window.alert(clickX+'');
    window.alert(clickY+'');
}

sayHello()
