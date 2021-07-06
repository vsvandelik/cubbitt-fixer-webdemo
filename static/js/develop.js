let CUBBITTFixerState = {
    loader: undefined,
    recalculatingFields: undefined,
    proximityFields: undefined,
    recalculatingToggle: undefined,
    proximityToggle: undefined,
    sourceLanguage: undefined,
    targetLanguage: undefined,
    customTranslation: undefined,
    originalTranslation: undefined,
    afterProcessingTranslation: undefined
};

$(function () {
    $('[data-toggle="tooltip"]').tooltip()

    // Translating
    CUBBITTFixerState.loader = $("#loader");
    CUBBITTFixerState.loader.hide();
    $("#translate button[type=submit]").click(translateInput);

    // Custom translation
    CUBBITTFixerState.customTranslation = $("#customOriginalTranslation")
        .change(swapEnableTranslationField);
    CUBBITTFixerState.originalTranslation = $("#originalTranslation");
    CUBBITTFixerState.afterProcessingTranslation = $("#afterPostprocessingTranslation");


    // Languages
    CUBBITTFixerState.sourceLanguage = $("#sourceLanguage")
        .change(_ => changedLanguage(CUBBITTFixerState.sourceLanguage, CUBBITTFixerState.targetLanguage));
    CUBBITTFixerState.targetLanguage = $("#targetLanguage")
        .change(_ => changedLanguage(CUBBITTFixerState.targetLanguage, CUBBITTFixerState.sourceLanguage));

    // Fields
    CUBBITTFixerState.recalculatingFields = $("#recalculateFields").hide();
    CUBBITTFixerState.proximityFields = $("#proximityFields").hide();
    CUBBITTFixerState.recalculatingToggle = $("#recalculate").click(_ => CUBBITTFixerState.recalculatingFields.toggle());
    CUBBITTFixerState.proximityToggle = $("#proximity").click(_ => CUBBITTFixerState.proximityFields.toggle());
});

function changedLanguage(me, opposite) {
    opposite.prop('selectedIndex', 1 - me.prop('selectedIndex'));
}

function swapEnableTranslationField(e) {
    if(e.target.checked)
        CUBBITTFixerState.originalTranslation.attr('disabled', false).focus();
    else
        CUBBITTFixerState.originalTranslation.val("").attr('disabled', true);



}

function translateInput(e) {
    e.preventDefault();

    CUBBITTFixerState.loader.show();

    let configuration = {
        source_text: $("#inputText").val(),
        source_lang: CUBBITTFixerState.sourceLanguage.val(),
        target_lang: CUBBITTFixerState.targetLanguage.val(),
        base_tolerance: $("#tolerance").val() / 100,
        tools: []
    };

    if (CUBBITTFixerState.recalculatingToggle.prop('checked')) {
        configuration.target_units = [];
        CUBBITTFixerState.recalculatingFields.find("select").each(function (i) {
            configuration.target_units.push($(this).val());
        });
        configuration.mode = 'recalculating';
    }

    if (CUBBITTFixerState.proximityToggle.prop('checked'))
        configuration.approximately_tolerance = $("input", CUBBITTFixerState.proximityFields).val() / 100;

    ["units", "separators", "names"].forEach(id => {
        if ($(`#${id}`).prop('checked'))
            configuration.tools.push(id);
    });

    if(CUBBITTFixerState.originalTranslation.val())
        configuration.target_text = CUBBITTFixerState.originalTranslation.val();

    $.post(
        `${$SCRIPT_ROOT}/fix`,
        configuration
    ).done(function (data) {
        if(!configuration.target_text)
            CUBBITTFixerState.originalTranslation.val(data.cubbitt);
        CUBBITTFixerState.afterProcessingTranslation.val(data.fixer);
    }).fail(function () {
        $("#translate").prepend('<div class="alert alert-danger">Cannot connect to lindat or postprocessor. Please try it later.</div>');
    }).always(function () {
        CUBBITTFixerState.loader.hide();
    });
}

