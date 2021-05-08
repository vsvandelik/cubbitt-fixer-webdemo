let CUBBITTFixerState = {
    loader: undefined,
    recalculatingFields: undefined,
    proximityFields: undefined,
    recalculatingToggle: undefined,
    proximityToggle: undefined,
    sourceLanguage: undefined,
    targetLanguage: undefined
};

$(function () {
    // Translating
    CUBBITTFixerState.loader = $("#loader");
    CUBBITTFixerState.loader.hide();
    $("#translate button[type=submit]").click(translateInput);

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
    }

    if (CUBBITTFixerState.proximityToggle.prop('checked'))
        configuration.approximately_tolerance = $("input", CUBBITTFixerState.proximityFields).val() / 100;

    ["units", "separators", "names"].forEach(id => {
        if ($(`#${id}`).prop('checked'))
            configuration.tools.push(id);
    });

    $.post(
        `https://lindat.mff.cuni.cz/services/translation/api/v2/languages/?src=${configuration.source_lang}&tgt=${configuration.target_lang}`,
        {input_text: configuration.source_text}
    ).done(function (data) {
            $("#originalTranslation").val(data);

            configuration.target_text = data;

            $.post(
                `${$SCRIPT_ROOT}/fix`,
                configuration
            ).done(function (data) {
                $("#afterPostprocessingTranslation").val(data);
            }).fail(function () {
                $("#translate").prepend('<div class="alert alert-danger">Cannot connect to postprocessor. Please try it later.</div>');
            });

        }
    ).fail(function () {
        $("#translate").prepend('<div class="alert alert-danger">Cannot connect to LINDAT translation service. Please try it later.</div>');
    }).always(function () {
        CUBBITTFixerState.loader.hide();
    });
}

