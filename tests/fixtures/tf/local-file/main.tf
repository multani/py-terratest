variable "content" {
  type    = string
  default = "foo"
}

resource "local_file" "foo" {
  content  = var.content
  filename = "${path.module}/test.txt"
}

output "filename" {
  value = local_file.foo.filename
}
