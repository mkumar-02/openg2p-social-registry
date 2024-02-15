// eslint-disable-next-line no-unused-vars,complexity
function formSubmitAction() {
    // URL Change
    var formContainer = $(".s_website_form");
    var programForm = formContainer.find("form");

    programForm[0].action = "/selfservice/submit";
    console.log(programForm[0].action);
    programForm[0].submit();
}
