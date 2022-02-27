<template>
  <div>
    <h4>提取文本</h4>

    <el-form v-show="extract.show" :model="extract" label-width="80px">
      <el-row :span="24">
        <el-col
          :xs="{ span: 10, offset: 6 }"
          :sm="{ span: 4, offset: 10 }"
          :md="{ span: 4, offset: 10 }"
          :lg="{ span: 3, offset: 10 }"
          :xl="{ span: 3, offset: 10 }"
        >
          <el-form-item label="提取码">
            <el-input
              v-model="extract.code"
              @keyup.enter="extractText"
            ></el-input>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <el-row v-show="!extract.show" :span="24">
      <el-col :offset="2" :span="20">
        <div>
          <p style="word-wrap: break-word; white-space: pre-wrap">
            {{ extract.text }}
          </p>
        </div>
      </el-col>
    </el-row>
    <el-row :span="24" class="topmargin">
      <el-col :offset="0" :span="24">
        <el-button
          v-show="extract.show"
          type="primary"
          plain
          @click="extractText"
          size="large"
          >提取</el-button
        >
        <el-button
          v-show="!extract.show"
          type="primary"
          plain
          @click="clipbord"
          size="large"
          >复制</el-button
        >
        <el-button
          v-show="!extract.show"
          type="primary"
          plain
          @click="backExtract"
          size="large"
          >再次提取</el-button
        >
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  data() {
    return {
      extract: {
        code: "",
        show: true,
        text: "",
      },
    };
  },
  methods: {
    extractText() {
      var _self = this;
      if (_self.extract.code == "") {
        _self.$message({
          message: "请输入提取码！",
          type: "warning",
        });
        return;
      }
      this.axios
        .post("/syncbackend/extract", {
          code: _self.extract.code,
        })
        .then(function (response) {
          if (response.data.code == 1) {
            _self.$message.error("提取失败!");
            return;
          }
          if (response.data.code == 2) {
            _self.$message({
              message: "提取文本不存在",
              type: "warning",
            });
            return;
          }
          _self.extract.text = response.data.result.text;
          _self.extract.show = false;

          _self.$copyText(_self.extract.text).then(
            function (e) {
              // console.log(e);
              _self.$message({
                message: "提取文本已复制到剪切板！",
                type: "success",
              });
            },
            function (e) {
              console.log(e);
            }
          );
        })
        .catch(function (error) {
          console.log(error);
          _self.$message.error("提取失败!");
        });
    },
    backExtract() {
      this.extract.show = true;
      // this.syncData.once = false;
      this.extract.code = "";
    },
    clipbord() {
      var _self = this;
      _self.$copyText(_self.extract.text).then(
        function (e) {
          // console.log(e);
          _self.$message({
            message: "提取文本已复制到剪切板！",
            type: "success",
          });
        },
        function (e) {
          console.log(e);
        }
      );
    },
  },
};
</script>

<style>
h4 {
  color: #303133;
}
.topmargin {
  margin-top: 20px;
}
</style>
