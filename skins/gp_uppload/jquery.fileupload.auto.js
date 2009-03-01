if (typeof(jQuery)!='undefined')
    jQuery(document).ready(function() {
        jQuery('form[enctype^="multipart/form-data"]').each(function(){
            if (jQuery('input:file', this).length > 0) {
                jQuery(this).fileUpload({use_iframes:false});
            }
        });
    });
