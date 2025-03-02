$(function() {
  $(".content_bio").each(function() {
    var $this = $(this);
    var originalText = $this.html();
    var prefixedOriginalText = "<strong>Bio:</strong> " + originalText;
    var shortenedText = prefixedOriginalText.substring(0, 204) + "...";
    if (originalText.length > 200) {
      $this.data('originalText', prefixedOriginalText);
      $this.data('shortenedText', shortenedText);
      $this.html(shortenedText);
      $this.after("<span class='toggle_text' style='color: blue; cursor: pointer;font-size: 0.8em;'>Read More</span>");
    } else {
      $this.html(prefixedOriginalText);
    }
  });
  $(document).on("click", ".toggle_text", function() {
    var $this = $(this);
    var $content = $this.prev(".content_bio");
    var originalText = $content.data('originalText');
    var shortenedText = $content.data('shortenedText');
    if ($content.html() === shortenedText) {
      $content.html(originalText);
      $this.text('Read Less');
    } else {
      $content.html(shortenedText);
      $this.text('Read More');
    }
  });
});
