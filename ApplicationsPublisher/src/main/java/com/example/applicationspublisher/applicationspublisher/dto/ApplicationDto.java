package com.example.applicationspublisher.applicationspublisher.dto;

public class ApplicationDto {
    private String fullName;
    private String phone;
    private String option;

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getOption() {
        return option;
    }

    public void setOption(String option) {
        this.option = option;
    }

    @Override
    public String toString() {
        return "ApplicationDto{" +
                "fullName='" + fullName + '\'' +
                ", phone='" + phone + '\'' +
                ", option='" + option + '\'' +
                '}';
    }
}