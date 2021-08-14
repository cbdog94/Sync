<template>
  <el-row>
    <el-col :offset="2" :span="20">
      <h4>上传文件</h4>
      <el-upload
        v-show="syncData.show"
        drag
        action="/syncbackend/upload"
        :on-success="uploadSuccess"
        :on-progress="uploadProcess"
        :on-error="uploadFailure"
        :show-file-list="false"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">
          将需要同步的文件拖到此处，或
          <em>点击上传</em>
        </div>
        <el-progress
          class="topmargin"
          v-show="progress.show"
          :percentage="progress.percentage"
          :show-text="true"
        ></el-progress>
      </el-upload>
      <p v-show="!syncData.show">
        提取码:
        <span style="color: #f56c6c; font-size: 18px">{{ syncData.code }}</span>
      </p>
    </el-col>
    <el-col :span="24">
      <el-button
        v-show="!syncData.show"
        class="topmargin"
        type="primary"
        plain
        @click="backsync"
        >再次上传</el-button
      >
    </el-col>
  </el-row>
</template>

<script>
export default {
  data() {
    return {
      progress: {
        show: false,
        percentage: 0,
      },
      syncData: {
        show: true,
        code: "",
      },
    };
  },
  methods: {
    backsync() {
      this.syncData.show = true;
      this.syncData.code = "";
    },
    uploadSuccess(response, file) {
      console.log(response);
      if (response.code != 0) {
        this.$message.error("上传失败!");
        console.log(response);
        return;
      }
      this.syncData.show = false;
      this.syncData.code = response.result.code;
      this.$message.success("上传成功!");
      this.progress.show = false;
      this.progress.percentage = 0;
    },
    uploadFailure(err, file, fileList) {
      console.log(err);
      this.$message.error("上传失败! " + err);
      this.progress.show = false;
      this.progress.percentage = 0;
    },
    uploadProcess(event, file, fileList) {
      this.progress.show = true;
      this.progress.percentage = Math.floor(event.percent);
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
p {
  color: #303133;
}
.el-upload {
  display: block;
}
.el-upload-dragger {
  width: auto;
}
</style>
