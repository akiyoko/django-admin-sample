(function($) {
    "use strict";
    $(document).ready(function() {
        $("#postal_code_search").on("click", function() {
            var postalCode = $("#id_postal_code_0").val() + $("#id_postal_code_1").val();
            $.ajax({
              type: "get",
              url: "/address/",
              dataType: "json",
              data: {
                postalCode: postalCode
              }
            })
            .done(function(data) {
                // 郵便番号コードに対応する住所が0件の場合
                if (data.length === 0) {
                    var dialogElement = $("<div>該当する住所が存在しません。</div>");
                    $(dialogElement).dialog({
                        title: '住所選択',
                        modal: true
                    });
                }
                // 郵便番号コードに対応する住所が1件の場合
                else if (data.length === 1) {
                    $("#id_prefecture").val(data[0].prefecture);
                    $("#id_address_1").val(data[0].city + data[0].town_area);
                    $("#id_address_2").val("");
                }
                // 郵便番号コードに対応する住所が複数件の場合
                else {
                    var dialogElement = $("<div>");
                    $.each(data, function(i) {
                        var address = this.prefecture + this.city + this.town_area;
                        var inputElement = $("<label>").append($("<input>").attr({
                            type: "radio",
                            name: "address",
                            value: i,
                            checked: i === 0
                        })).append(" " + address + "<br>");
                        dialogElement.append(inputElement);
                    });
                    $(dialogElement).dialog({
                        title: '住所選択',
                        modal: true,
                        buttons: {
                            'OK': function () {
                                var i = $('input[name="address"]:checked').val();
                                $("#id_prefecture").val(data[i].prefecture);
                                $("#id_address_1").val(data[i].city + data[i].town_area);
                                $("#id_address_2").val("");
                                $(this).dialog('close');
                            }
                        }
                    });
                }
            });
        });
    });
}(django.jQuery || jQuery));
