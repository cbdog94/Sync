<template>
  <div>
    <h4>提取文件</h4>

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
              @keyup.enter="extractFile"
            ></el-input>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <el-row :span="24" class="topmargin">
      <el-col :offset="0" :span="24">
        <el-button
          v-show="extract.show"
          type="primary"
          plain
          @click="extractFile"
          size="large"
          >提取</el-button
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
import fileDownload from "js-file-download";
export default {
  data() {
    return {
      extract: {
        code: "",
        show: true,
      },
    };
  },
  methods: {
    extractFile() {
      var _self = this;
      if (_self.extract.code == "") {
        _self.$message({
          message: "请输入提取码！",
          type: "warning",
        });
        return;
      }
      this.axios
        .get("/syncbackend/checkfile/" + _self.extract.code)
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
          _self.axios
            .get("/syncbackend/download/" + _self.extract.code, {
              responseType: "blob",
            })
            .then((res) => {
              fileDownload(res.data, response.data.result.filename);
              _self.$message.success("提取成功!");
              _self.extract.show = false;
            });
        })
        .catch(function (error) {
          console.log(error);
          _self.$message.error("提取失败!");
        });
    },
    backExtract() {
      this.extract.show = true;
      this.extract.code = "";
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
