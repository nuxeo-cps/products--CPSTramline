/* file upload progress bar */
if (typeof(jQuery)!='undefined') {

var FileUploadRegistry = {
    wrappers: new Array(),
    forms: {}
};

(function($) {

$.fn.fileUpload = function(options) {

    // default settings
    var action = document.location.href.split('#')[0].split('?')[0];
    var settings = $.extend({
        replace_existing_form: false,
        add_submit: true,
        submit_label: 'Send files',
        hidden_submit_name: 'submit_button',
        max_size_error_label: 'File is too big',
        field_name: 'file',
        submit_empty_forms: true,
        use_iframes: true,
        stat_url: action+'/gp.fileupload.stat/',
        stat_delay: 1500,
        stat_timeout: 7000,
        success: function() {},
        error: function() {},
        action: action
    }, options);

    // console logging
    var log = {
        info: function(message) {
            if (settings.debug) {
                if (window.console)
                    window.console.info(message);
            }
        },
        warn: function(message) {
            if (settings.debug) {
                if (window.console)
                    window.console.warn(message);
            }
        }
    }

    if (settings.hidden_submit_name == 'submit')
        log.warn("Don't set the hidden_submit_name options to 'submit'");
    
    var Wrapper = function(element) {
        // Wrapper class
        this.element = element;
        this.settings = settings;
        this.forms = new Array();
        this.forms_wrapper = $('<div></div>')
                                .appendTo(element);
    }

    $.extend(Wrapper.prototype, {
        // Wrapper methods
        initialize: function() {
            var self = this;
            var empty = true;
            if (self.settings.replace_existing_form == true) {
                this.forms_wrapper.prev().remove()
            }
            $('form', this.element).each(function() {
                if (!$(this).hasClass('fuForm')) {
                    self.forms.push(new Form(this, self));
                } else {
                    empty = false;
                }
            });
            if (empty && self.forms.length == 0 || self.settings.replace_existing_form) {
                // show form
                self.showNext();

                // add submit
                var submit = '<input class="fuButton" type="submit" ' +
                                     'name="'+settings.hidden_submit_name+'" />';
                $(submit)
                    .appendTo(self.element)
                    .val(self.settings.submit_label)
                    .click(function() {
                        self.submit();
                    });
            }
        },
        showNext: function() {
            var self = this;
            var form = $('' +
                '<form class="fuForm fuLastForm" method="POST" ' +
                      'enctype="multipart/form-data" ' +
                      'action="'+this.settings.action+'"> ' +
                    '<input type="file" value="" ' +
                           'name="'+this.settings.field_name+'" /> ' +
                    '<input type="hidden" ' +
                           'value="'+this.settings.submit_label+'" ' +
                           'name="'+this.settings.hidden_submit_name+'" />' +
                '</form>').appendTo(this.forms_wrapper);

            $('input:file', form).change(function() {
                if (form.hasClass('fuLastForm')) {
                    form.removeClass('fuLastForm');
                    self.showNext();
                }
            });
            this.forms.push(new Form(form, this));
        },
        submit: function() {
            var self = this;

            $('.fuButton', self.element).css('display', 'none');

            $(self.forms).each(function(i, item) {
                var form = item.form;

                if ($(form).hasClass('fuLastForm')) {
                    log.info("Don't submit last form "+item.id);
                    item.submit = false;
                    $(form).remove();
                    return;
                }

                // hide form
                $(form).css('display','none');

                // check filenames
                var filenames = '';
                $('input:file', form).each(function() {
                    var filename = $(this).val();
                    if (filename) {
                        // clean filename
                        if (filename.match('/'))
                            // unix path
                            filename = filename.split('/').pop();
                        if (filename.match('\\\\'))
                            // windows path
                            filename = filename.split('\\').pop();

                        // concat
                        if (filenames != '') {
                            filenames += ' - '+filename;
                        } else {
                            filenames = filename;
                        }
                    }
                });

                if (filenames) {
                    // show progress bar and change target only if we have some files

                    // add progress bar
                    var progress = '' +
                        '<div class="fuWrapper">' +
                            '<div class="fuFilename">'+filenames+'</div>' +
                            '<div style="position:relative">' +
                                '<span style="float:left;" ' +
                                      'class="fuProgress">&nbsp;</span><br />' +
                            '</div></div>';
                    progress = $(progress).appendTo(item.wrapper.element);
                    item.progress = $('.fuProgress', progress);

                    if (self.settings.use_iframes) {
                        // add iframe
                        var target = '<iframe style="display:none" ' +
                                             'src="about:blank" ' +
                                             'name="iframe_'+item.id+'">' +
                                     '</iframe>';
                        $(target).appendTo(item.wrapper.element);

                        // change target
                        $(form).attr('target', 'iframe_'+item.id);
                        log.info('Submiting form '+item.id+' to iframe');
                    }

                } else {
                    if (!self.settings.submit_empty_forms)
                        // dont submit empty form
                        item.submit = false;
                }
            });
            self.submitNext();
        },
        submitNext: function() {
            if (this.forms.length > 0) {
                var item = this.forms.shift();
                if (item.submit) {
                    item.form.submit();
                    item.setTimeout();
                    log.info('Form '+item.id+' submited');
                } else {
                    log.info('Skipping form '+item.id);
                    this.submitNext();
                }
            } else {
                this.settings.success();
            }
        }
    });

    var Form = function(form, wrapper) {
        // Form class
        var id = ''+Math.random()*10000000000000000000;
        this.id = id;
        this.submit = true;
        this.retries = 0;
        this.form = form;
        this.wrapper = wrapper;
        this.progress = null;
        this.max_retries = 5;

        // register form
        FileUploadRegistry.forms[id] = this;

        // add session to form action
        var action = $(form).attr('action');
        if (action.match('\\?')) {
            action += '&gp.fileupload.id='+id;
        } else {
            action += '?gp.fileupload.id='+id;
        }

        log.info('Form '+id+' '+action+' registered');

        // set form attributes
        $(form)
            .addClass('fuForm')
            .attr('id', id)
            .attr('action', action)
            .attr('method', 'POST')
            .attr('enctype', 'multipart/form-data')
            .wrap('<div></div>');

        // bind click on existing form
        $('input[type^="submit"]', form)
            .addClass('fuButton')
            .click(function() { wrapper.submit(); });
    }

    $.extend(Form.prototype, {
        // Form methods
        setTimeout: function(delay) {
            if (!delay)
                delay = this.wrapper.settings.stat_delay;
            setTimeout('FileUploadRegistry.forms["'+this.id+'"].stat()', delay);
        },
        stat: function() {
            // get stats for a session
            var self = this;
            var query = '?q='+Math.random()*10000000000000000000;
            var max_size_error = self.wrapper.settings.max_size_error_label;
            $.ajax({
                 type: 'GET',
                 dataType: 'json',
                 timeout: self.wrapper.settings.stat_timeout,
                 url: self.wrapper.settings.stat_url+self.id+query,
                 success: function(response) {
                        if (response.state == -1) {
                            // upload failure
                            self.progress.css('width','100%')
                                         .addClass('fuProgressFailure')
                                         .html(max_size_error);
                            self.wrapper.submitNext();
                            return;
                        }
                        if (response.state == 0) {
                            // not started
                            self.retries += 1;
                            if (self.retries > self.max_retries) {
                                self.progress.css('width','100%')
                                             .addClass('fuProgressFailure')
                                             .html('&nbsp;');
                                self.wrapper.submitNext();
                            } else {
                                self.setTimeout(300);
                            }
                            return;
                        } else {
                            self.retries = 0;
                        }
                        if (response.percent >= 0 && response.percent < 100) {
                            // progress
                            self.progress.css('width',response.percent+'%')
                                         .html(response.percent+'%');
                            self.setTimeout();
                        }
                        if (response.percent == 100) {
                            // upload success
                            self.progress.css('width','100%')
                                         .addClass('fuProgressSuccess')
                                         .html(response.percent+'%')
                                         .removeClass('fuProgress');
                            self.wrapper.submitNext();
                        }
                 },
                 error: function(response) {
                     self.retries += 1;
                     if (self.retries > 3) {
                         self.progress.css('width','100%')
                                      .addClass('fuProgressFailure')
                                      .html('&nbsp;');
                         self.wrapper.submitNext();
                     } else {
                        self.setTimeout(500);
                     }
                 }
            }); 
        }
    });
    return this.each(function(i, item) {
        if ($(item).attr('enctype') == 'multipart/form-data')
            // we have an existing form so wrap it
            item = $(item).wrap('<div></div>').parent();
        var wrapper = new Wrapper(item);
        wrapper.initialize();
        FileUploadRegistry.wrappers.push(wrapper);
    });
}

})(jQuery);

}
